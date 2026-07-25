"""트렌드 픽 레인 — 링크 선별·스로틀·포트폴리오 게시 산출물.

카드뉴스와 완전 분리된 경로(사서·위키 안 탐). _publish_trend는 발송 성공
후에만 불리며 어떤 실패도 삼킨다.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import cardgen
import dedup as dedup_lib

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
    """'오늘의 트렌드' 링크 선별 — 카드·위키·사서를 타지 않는 결정적 경로.

    소스별로 (score 내림차순 → published 내림차순) 정렬 후 라운드로빈으로
    상한까지 뽑는다 — 한 소스(예: HN 검색)가 섹션을 독식하지 않게 하는
    다양성 장치. 점수 체계가 소스마다 달라(HN points vs 레딧 무점수 RSS)
    전역 정렬은 의미가 없다. URL 정규화 중복은 먼저 접는다."""
    cap = int(config.get("trend_max_links", 6))
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

    selected: list[dict] = []
    # 큐 우선순위 = 사용자 관심축(QA2: 관심축 가중치) — 상한(cap)보다
    # 그룹이 많을 때 어떤 그룹이 슬롯을 얻는지 결정한다. 미등재 그룹은 뒤
    priority = {g: i for i, g in enumerate(config.get("trend_priority", []))}
    queues = [g for _, g in sorted(
        ((priority.get(k, len(priority)), g)
         for k, g in by_source.items() if g),
        key=lambda pair: pair[0],
    )]
    while queues and len(selected) < cap:
        next_queues = []
        for group in queues:
            if len(selected) >= cap:
                break
            while group:
                cand = group.pop(0)
                # 이미 뽑힌 항목과 같은 사건/소식(제목 토큰·CVE 유사도)이면
                # 건너뛰고 그룹의 다음 후보로 — 구글뉴스 재보도 vs 공식
                # 원문이 다른 그룹에서 둘 다 뽑히는 것 방지
                if any(dedup_lib.is_similar_event(cand, s) for s in selected):
                    continue
                selected.append(cand)
                break
            if group:
                next_queues.append(group)
        queues = next_queues
    return selected


TREND_SEND_HOURS = (8, 23)  # KST — 심야 트렌드 알림은 소음(긴급 아님)


def _should_send_trend(state: dict, now_kst: datetime, config: dict) -> bool:
    """트렌드 알림 스로틀 — 사용자 요구: 너무 자주 오면 본편을 가린다.

    ① KST 08~23시 밖이면 보류(심야 금지), ② 마지막 발송 후
    trend_interval_hours(기본 6시간)가 지나야 다시 보낸다 → 하루 최대
    2~3회. 보류된 후보는 seen에 남기지 않아(main 하단) 다음 run이
    같은 항목을 다시 가져와 재도전한다 — 별도 대기열 상태 파일이 필요
    없고, top?t=day·HN 최근 2일 창이 '아직 핫한 것'만 자연 유지한다."""
    if not (TREND_SEND_HOURS[0] <= now_kst.hour < TREND_SEND_HOURS[1]):
        return False
    last = state.get("last_trend_sent")
    if not last:
        return True
    interval = timedelta(hours=float(config.get("trend_interval_hours", 6)))
    try:
        return datetime.now(timezone.utc) - datetime.fromisoformat(last) >= interval
    except (TypeError, ValueError):
        return True  # 손상된 타임스탬프는 발송 허용(fail-open) 후 덮어쓴다


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
