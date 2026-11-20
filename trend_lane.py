"""트렌드 픽 레인 — 링크 선별·발송·포트폴리오 게시 산출물.

선별·주석 경로는 여전히 카드뉴스와 분리돼 있다(사서·위키·judge 안 탐).
발송 '시점'만 아침 카드뉴스 발행 직후로 묶어 하루 1회로 제한한다
(2026-08-13 사용자 피드백: 하루 여러 번은 넘겨 버리게 된다).
_publish_trend는 카드뉴스 발송 성공 후에만 불리며 어떤 실패도 삼킨다.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import cardgen
import dedup as dedup_lib
import notify
import trend_enrich

from common import TREND_DIR, _safe_exc_str


def _normalize_trend_url(url: str) -> str:
    # HN·Lobsters가 같은 원문을 동시에 띄우는 경우의 링크 중복 키 —
    # 스킴·www·꼬리 슬래시 차이만 접는다(쿼리는 유지: 유튜브 watch?v=)
    u = url.lower()
    for prefix in ("https://", "http://"):
        if u.startswith(prefix):
            u = u[len(prefix):]
            break
    if u.startswith("www."):
        u = u[4:]
    return u.rstrip("/")


def _select_trend(items: list[dict], config: dict) -> list[dict]:
    """트렌드 선정 후보 풀 — 카드·위키·사서를 타지 않는 결정적 경로.

    2026-11-20 개편: 이 함수는 더 이상 발송 목록을 확정하지 않는다. 그룹별
    상위 trend_pool_per_group건씩 모은 후보 풀을 돌려주고, 최종 최대 2건은
    발송 직전 trend_enrich.pick이 풀 전체를 보고 고른다(구 라운드로빈은
    출처를 골고루 채울 뿐 중요한 것을 고르지 못했다). 정렬 기준은 그대로:
    그룹 안에서 score 내림차순, 같은 소식이면 공식 원문 우선. URL 정규화
    중복과 같은 사건 중복은 풀 단계에서 먼저 접는다."""
    per_group = int(config.get("trend_pool_per_group", 8))
    seen_urls: set[str] = set()
    by_source: dict[str, list[dict]] = {}
    for item in items:
        url = item.get("url") or ""
        key = _normalize_trend_url(url)
        if not url or key in seen_urls:
            continue
        # 유튜브 쇼츠는 본편 영상 대비 정보량이 낮은 클립이 대부분 —
        # 링크 5석을 소모할 가치가 없다(2026-07-24 실발송 검수에서 제외 결정)
        if "youtube.com/shorts/" in key:
            continue
        seen_urls.add(key)
        group_key = item.get("trend_group") or item.get("source", "")
        by_source.setdefault(group_key, []).append(item)

    for group in by_source.values():
        # 안정 정렬 3단: published 내림차순 → 구글뉴스 리다이렉트 후순위
        # (같은 소식이면 벤더 공식 원문이 이긴다) → score 내림차순(주 기준)
        group.sort(key=lambda it: it.get("published") or "", reverse=True)
        group.sort(key=lambda it: "news.google.com" in (it.get("url") or ""))
        group.sort(key=lambda it: -(it.get("score") or 0))

    pool: list[dict] = []
    # 풀 나열 순서 = 사용자 관심축(trend_priority). LLM 선정에 순서 가중은
    # 없지만 프롬프트에서 관심축 후보가 앞에 오게 한다. 미등재 그룹은 뒤
    priority = {g: i for i, g in enumerate(config.get("trend_priority", []))}
    ordered = sorted(by_source.items(),
                     key=lambda kv: priority.get(kv[0], len(priority)))
    for _, group in ordered:
        taken = 0
        for cand in group:
            if taken >= per_group:
                break
            # 이미 풀에 든 항목과 같은 사건/소식이면 건너뛴다 — 구글뉴스
            # 재보도와 공식 원문이 다른 그룹에서 둘 다 들어오는 것 방지
            if any(dedup_lib.is_similar_event(cand, s) for s in pool):
                continue
            pool.append(cand)
            taken += 1
    return pool


def _should_send_trend(state: dict, now_kst: datetime, run_mode: str) -> bool:
    """트렌드 픽 발송 게이트 — 하루 1회, 아침 카드뉴스와 동반.

    구 설계는 6시간 스로틀(KST 08~23시)이라 하루 2~3회가 나갔고, 사용자
    피드백(2026-08-13)은 "계속 넘기고 안 보게 된다"였다. 알림 가치는
    빈도가 아니라 '펼쳐 볼 시점에 한 번'에서 나오므로, 아침 카드뉴스가
    실제로 발행되는 run에 묶어 하루 1회만 내보낸다.

    ① run_mode == digest 인 run에서만 참 — 카드뉴스 발행 경로와 같은 run.
    ② 오늘(KST) 이미 보냈으면 거짓 — force_digest 재발행이 트렌드까지
       중복으로 밀어내지 않게 하는 가드.
    실제 발송은 카드뉴스 발행이 확정된 뒤 send_daily_trend가 수행한다.

    [긴급] 알림 레인은 이 게이트와 무관하다 — 대형 사건은 judge가 판정해
    즉시 개별 카드로 나가며(main.card_items), 트렌드는 애초에 긴급 판정
    대상이 아니다. 즉 이 변경으로 느려지는 것은 '화제글'뿐이다.

    보류된 후보는 seen에 남기지 않아(main 하단) 다음 run이 같은 항목을
    다시 가져온다 — 별도 대기열 상태 파일이 필요 없고, top?t=day·HN
    최근 2일 창이 '아침에 아직 핫한 것'만 자연 유지한다."""
    if run_mode != "digest":
        return False
    return state.get("last_trend_date") != now_kst.strftime("%Y-%m-%d")


def send_daily_trend(
    pool: list[dict],
    discord_cfg: dict,
    state: dict,
    today_kst: str,
) -> bool:
    """카드뉴스 발행 확정 직후의 트렌드 픽 1일 1회 발송. 처리 완료 시 True.

    pool(_select_trend 후보 풀)에서 trend_enrich.pick이 최대 2건을 고르고
    한국어 제목·설명을 쓴다. 볼 만한 게 0건이면 아무것도 보내지 않고
    True(후보 소진) — 다음 날 같은 후보가 다시 올라오지 않게 한다.

    선정 LLM 실패·발송 예외는 False: 호출 측(main)이 후보를 seen에 남기지
    않아 다음 날 아침 자연 재도전한다. 영어 원제로 폴백 발송하지 않는다.

    last_trend_date는 처리 완료 뒤에만 기록한다: digest 자체가 하루 1회
    가드(last_digest_date)를 이미 통과한 run이라 같은 날 재진입이 없어
    중복 발송 위험이 없고, 선기록하면 실패한 날의 트렌드가 통째로
    사라진다."""
    try:
        picks = trend_enrich.pick(pool)
        if picks is None:
            print("[main] 트렌드 선정 실패 — 오늘은 보내지 않음(내일 재도전)",
                  file=sys.stderr)
            return False
        if picks:
            notify.send_trend(picks, discord_cfg)
        state["last_trend_date"] = today_kst
        print(f"[main] 트렌드 픽(하루 1회): 후보 {len(pool)}건 중 {len(picks)}건 발송")
        return True
    except Exception as exc:
        print(f"[main] 트렌드 발송 실패(내일 아침 재도전): {_safe_exc_str(exc)}",
              file=sys.stderr)
        return False


def _publish_trend(
    pngs: list[bytes],
    ordered_items: list[dict],
    issue_no: int | None,
    briefing: str | None,
    keywords: list[str],
) -> None:
    """포트폴리오 Trend 탭 게시용 PNG + meta.json 저장.

    ordered_items는 카드 표시 순서(뉴스 → 그 밖의 소식 → 오늘의 CVE)와
    동일해야 links 번호가 build_link_lines와 1:1로 맞는다. 발송이 이미
    성공한 뒤에 불리므로 어떤 실패도 삼킨다 — 사이트 게시 실패가 아침
    브리핑 파이프라인(폴백 이중발송 포함)을 건드리면 안 된다."""
    try:
        os.makedirs(TREND_DIR, exist_ok=True)
        names = []
        for i, png in enumerate(pngs, start=1):
            name = f"card_{i:02d}.png"
            with open(os.path.join(TREND_DIR, name), "wb") as f:
                f.write(png)
            names.append(name)
        # JPEG 사본 — 인스타그램 Graph API가 JPEG만 받는다(crosspost.py가
        # github.io에 배포된 이 사본의 URL로 발행). 변환 실패는 크로스포스트만
        # 포기(fail-open) — Pillow는 requirements에 있으나 방어적으로 감싼다
        jpg_names = []
        try:
            from io import BytesIO

            from PIL import Image
            for i, png in enumerate(pngs, start=1):
                jpg_name = f"card_{i:02d}.jpg"
                Image.open(BytesIO(png)).convert("RGB").save(
                    os.path.join(TREND_DIR, jpg_name), "JPEG",
                    quality=92, optimize=True)
                jpg_names.append(jpg_name)
        except Exception as exc:
            jpg_names = []
            print(f"[main] JPEG 변환 실패(크로스포스트만 스킵): {_safe_exc_str(exc)}",
                  file=sys.stderr)
        kst = timezone(timedelta(hours=9))
        meta = {
            "date": datetime.now(kst).strftime("%Y-%m-%d"),
            "issue_no": issue_no,
            "briefing": briefing,
            "keywords": keywords,
            "links": [
                {
                    # 라벨은 Discord 링크 목록과 동일 규칙(cardgen.link_label):
                    # title_ko 우선·CVE는 ID — 카드 본문 제목과 일치해야 한다
                    "n": i,
                    "title": cardgen.link_label(it),
                    "url": it.get("url", ""),
                }
                for i, it in enumerate(ordered_items, start=1)
            ],
            "cards": names,
            # 크로스포스트(IG/Threads)용 JPEG 사본 — crosspost.py가 참조
            "cards_jpg": jpg_names,
        }
        with open(os.path.join(TREND_DIR, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"[main] trend 게시 산출물 저장: out/trend ({len(names)}장)")
    except Exception as exc:
        print(f"[main] trend 산출물 저장 실패(무시): {_safe_exc_str(exc)}", file=sys.stderr)
