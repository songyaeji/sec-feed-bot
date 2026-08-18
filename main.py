"""Entry point orchestration: fetch -> filter -> dedup -> notify -> persist.

Run by GitHub Actions every ~10 minutes (external cron-job.org trigger
via workflow_dispatch — see docs/external-trigger.md; an hourly schedule
cron is the fallback). This script only writes state/seen.json locally;
the workflow (not this script) is responsible for committing that file
back to the repo.

로직은 응집 그룹별 모듈로 분리돼 있다(2026-07-25 분할): common(경로·마스킹)
/ state_store(상태 I/O) / collect(소스 수집) / digest_select(카드 선별) /
wiki_index(INDEX 정리) / trend_lane(트렌드 픽). main()은 흐름 조립만 맡는다.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import cardgen
import dedup as dedup_lib
import judge
import librarian
import notify
import preflight
import tagger
from collect import collect_all, dedup, max_items_per_run
from common import STATE_DIR, _safe_exc_str
from digest_select import (
    _apply_dedup_groups, _author_penalty, _backfill_news, _dedup_by_topic,
    _dedup_similar, _fallback_keywords, _issue_no, _source_regions,
    _split_fresh)
from state_store import (  # noqa: F401 -- SEEN_TTL_DAYS는 tests가 main 경유로 참조
    SEEN_TTL_DAYS, append_pending, load_config, load_pending, load_state,
    prune_seen, save_pending, save_state)
from trend_lane import (_publish_trend, _select_trend, _should_send_trend,
                        send_daily_trend)
from wiki_index import _prune_wiki_index

# 크로스포스트(인스타/쓰레드)는 crosspost.py CLI로 분리됐다 — Instagram
# Graph API가 '공개 URL + JPEG'만 받아 디스코드 첨부(PNG)로는 발행이
# 불가능하기 때문. collect.yml이 포트폴리오 push 후 crosspost.py를
# 별도 스텝으로 실행한다(_publish_trend가 JPEG 사본과 meta를 남긴다).

SEVERITY_ORDER = {"critical": 0, "high": 1, "info": 2}


def _print_dry_run_stats(card_items: list[dict], non_urgent_items: list[dict]) -> None:
    # DRY_RUN skips notify.send_cards()/send_digest() entirely, so this
    # mirrors the routing decision they would have made (individual card
    # vs. digest bucket) and the tag hit-rate, purely for local verification.
    tag_counts: dict[str, int] = {}
    for item in card_items + non_urgent_items:
        for tag in item.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    print(f"[main] tag counts: {tag_counts}")

    print(f"[main] urgent -> individual card: {len(card_items)}건")
    category_counts: dict[str, int] = {}
    for item in non_urgent_items:
        category_counts[item.get("category")] = category_counts.get(item.get("category"), 0) + 1
    for category, count in category_counts.items():
        print(f"[main] non-urgent category '{category}': {count}건 -> digest")


def _save_preview_cards(
    merged: list[dict], card_items: list[dict], discord_cfg: dict,
    issue_no: int | None = None,
    regions: dict[str, str] | None = None,
) -> None:
    # DRY_RUN digest에서도 렌더 경로를 실제로 태워 PNG를 남긴다 —
    # 전송 없이 로컬에서 카드 디자인을 눈으로 검수하기 위한 용도라서
    # 렌더 실패(playwright 미설치 등)는 경고만 하고 run을 깨지 않는다.
    # 사서(librarian)는 DRY_RUN에서 돌지 않으므로 briefing/wiki_new 없음.
    # 트렌드는 카드가 아니라 링크 섹션 전용 — 카드 렌더에서 제외
    merged = [it for it in merged if it.get("category") != "trend"]
    if not merged:
        return
    try:
        stats = {
            "total": len(merged),
            "urgent": len(card_items),
            "finance": sum(1 for it in merged if "금융" in (it.get("tags") or [])),
        }
        # DRY_RUN은 회차를 증가시키지 않고 현재값(다음에 나갈 번호)만 표기
        if issue_no is not None:
            stats["issue_no"] = issue_no
        stats["keywords"] = _fallback_keywords(merged)
        pngs = cardgen.build_cards(
            merged, briefing=None, stats=stats,
            colors=discord_cfg.get("colors", {}),
            regions=regions,
        )
        preview_dir = os.path.join(STATE_DIR, "preview")
        os.makedirs(preview_dir, exist_ok=True)
        for i, png in enumerate(pngs, start=1):
            with open(os.path.join(preview_dir, f"card_{i:02d}.png"), "wb") as f:
                f.write(png)
        print(f"[main] DRY_RUN: 카드뉴스 {len(pngs)}장 -> state/preview/ 저장")
        # 포트폴리오 게시 산출물도 함께 남긴다 — Trend 페이지 레이아웃을
        # 실제 발송 없이 로컬에서 검증하기 위한 경로
        top, cve_rest, other_rest = cardgen.plan_cards(merged)
        _publish_trend(
            pngs, top + other_rest + cve_rest,
            issue_no=stats.get("issue_no"), briefing=None,
            keywords=stats.get("keywords") or [],
        )
    except Exception as exc:
        print(f"[main] DRY_RUN: 카드뉴스 렌더 실패(경고만): {_safe_exc_str(exc)}", file=sys.stderr)


def main() -> None:
    config = load_config()
    state = load_state()

    run_mode = os.environ.get("RUN_MODE", "realtime")
    if run_mode not in ("realtime", "digest"):
        print(f"[main] unknown RUN_MODE '{run_mode}', falling back to 'realtime'", file=sys.stderr)
        run_mode = "realtime"

    # digest 이중발행 가드 — digest는 외부 트리거(cron-job.org)와 GitHub
    # schedule cron 두 경로로 발화한다(후자는 지연이 커서 안전망으로만 유지,
    # docs/external-trigger.md). 같은 날 두 번째 digest는 realtime으로
    # 강등해 카드뉴스·issue_no 이중 발행을 막는다. 발행 실패 시에는
    # last_digest_date가 안 남아 늦게 온 cron이 자연스럽게 재시도가 된다.
    # FORCE_DIGEST=1: 사람이 Actions UI/CLI로 명시한 같은 날 재발행 —
    # state의 last_digest_date를 손으로 되감는 방식은 merge_state의
    # max() union이 동시 실행 중인 realtime 커밋에서 오늘 날짜를 부활시켜
    # 레이스로 무산된다(2026-07-13 실측). 가드 우회 플래그가 레이스 프리.
    now_kst = datetime.now(timezone(timedelta(hours=9)))
    today_kst = now_kst.strftime("%Y-%m-%d")
    force_digest = os.environ.get("FORCE_DIGEST") == "1"
    if (
        run_mode == "digest"
        and state.get("last_digest_date") == today_kst
        and not force_digest
    ):
        print(
            f"[main] 오늘({today_kst}) digest 이미 발행됨 — realtime으로 강등",
            file=sys.stderr,
        )
        run_mode = "realtime"

    # digest 발행 시간창 가드 — 외부 트리거 payload 오설정(2026-07-12:
    # realtime 잡이 mode=digest를 보내 KST 자정 직후 00:23에 발행됨)에
    # 대한 2차 방어. 아침 발행(06:50 예약 + Actions 지연 여유)만 허용하고
    # 그 밖의 시각에 도착한 digest는 realtime으로 강등한다.
    # 수동 테스트 등 의도적 심야 발행은 ALLOW_OFFHOUR_DIGEST=1로 우회.
    if (
        run_mode == "digest"
        and not (6 <= now_kst.hour < 12)
        and os.environ.get("ALLOW_OFFHOUR_DIGEST") != "1"
        and not force_digest
    ):
        print(
            f"[main] digest 허용 시간창(KST 06~12시) 밖({now_kst.strftime('%H:%M')}) "
            "— realtime으로 강등 (우회: ALLOW_OFFHOUR_DIGEST=1)",
            file=sys.stderr,
        )
        run_mode = "realtime"

    all_items = collect_all(config, state)
    new_items = dedup(all_items, state["seen"])

    tag_rules = config.get("tags", {})
    for item in new_items:
        tagger.tag_item(item, tag_rules)

    # 1st layer: heuristic cross-source duplicate detection. id-based
    # dedup() above only catches an exact re-fetch of the same URL/CVE id;
    # this catches the same event reported by a *different* outlet (same
    # CVE, or a near-identical headline). Duplicates are still marked seen
    # below (via new_items, unfiltered) so they don't come back through
    # id-based dedup either, but they never reach urgent/pending routing.
    dedup_lib.ensure_dedup_state(state)
    routable_items = []
    cross_dup_count = 0
    for item in new_items:
        # trend는 교차중복 검사·기록을 우회한다 — 보류(스로틀) 시 seen에
        # 남기지 않고 다음 run이 재수집하는 설계라, 여기서 자기 자신의
        # 기록에 걸려 두 번째 수집이 중복으로 죽으면 안 된다. 트렌드 내부
        # 중복은 _select_trend의 URL 정규화가 거른다
        if item.get("category") != "trend":
            if dedup_lib.is_cross_duplicate(item, state):
                cross_dup_count += 1
                continue
            dedup_lib.record_alerted(item, state)
        routable_items.append(item)
    if cross_dup_count:
        print(f"[main] 교차중복 {cross_dup_count}건 스킵", file=sys.stderr)

    routable_items.sort(key=lambda it: SEVERITY_ORDER.get(it["severity"], 99))

    # v8: "긴급" = 대형 사건·사고만 (judge.py 하이브리드 판정 — 키워드
    # 게이트 + sonnet). 구 기준(KEV/CVSS≥9/긴급 소스)은 폐기: 그런 항목도
    # 아침 다이제스트로 몰아 보낸다. DRY_RUN은 LLM 호출 없이 게이트만 로그.
    dry_run = os.environ.get("DRY_RUN") == "1"
    # 트렌드는 긴급 판정 대상이 아니다(커뮤니티 화제글 ≠ 확인된 사건;
    # 초기 신호는 breaking HN front_page 소스가 이미 커버) — judge
    # 키워드 게이트·LLM 예산에서 제외하고 독립 알림 레인으로 뺀다
    trend_candidates = [
        it for it in routable_items if it.get("category") == "trend"]
    judge_input = [
        it for it in routable_items if it.get("category") != "trend"]
    urgent_items = judge.select_urgent(judge_input, config, allow_llm=not dry_run)
    urgent_ids = {it["id"] for it in urgent_items}
    # breaking 소스(HN·레딧)는 즉시 발송 후보로만 쓴다 — 긴급이 아니면
    # 다이제스트에 싣지 않고 버린다 (seen에는 남아 재등장하지 않는다)
    non_urgent_items = [
        it for it in judge_input
        if it["id"] not in urgent_ids and not it.get("breaking")
    ]
    dropped_breaking = len(judge_input) - len(urgent_items) - len(non_urgent_items)
    if dropped_breaking:
        print(f"[main] breaking 소스 비긴급 {dropped_breaking}건 버림", file=sys.stderr)

    # cap what we send as individual cards, but still mark everything as
    # seen below so the overflow is not re-sent on the next run
    card_items = urgent_items
    cap = max_items_per_run(config)
    if cap is not None and len(urgent_items) > cap:
        card_items = urgent_items[:cap]
        print(f"{len(urgent_items) - cap}건 생략(개별 카드 상한 초과)")

    pending = load_pending()
    discord_cfg = config.get("discord", {})

    # ── 트렌드 픽 레인 — 하루 1회, 아침 카드뉴스 발행과 동반 ────────────
    # 핫한 AI 툴·skills·MCP·영상·글을 별도 embed 1건으로 알린다. 선별·
    # 주석 경로는 카드뉴스와 여전히 분리(사서·위키·judge 미경유)이고,
    # 발송 '시점'만 카드뉴스 발행 직후로 묶는다(_should_send_trend).
    # 여기서는 후보 선별까지만 하고 실제 발송은 발행 확정 뒤로 미룬다 —
    # 카드뉴스가 그날 안 나가면 트렌드도 안 나가는 것이 사용자 의도.
    # 게이트에 걸렸거나 발송 전인 후보는 seen에 남기지 않아(아래 state
    # 기록부) 다음 run이 재수집·재도전한다 — 대기열 파일 없음.
    # 발송 성공 시에는 미선발 후보까지 전량 seen 소진한다(의도된 정책:
    # 같은 항목이 다음 날 재선별 후보로 돌아와 반복 노출되는 소음 방지 —
    # 선발 경쟁에서 진 항목은 그 시점 화제성이 부족했던 것).
    # [긴급] 레인은 이 변경과 무관하다 — judge가 판정한 대형 사건은
    # 종전대로 run 즉시 개별 카드(card_items)로 나간다.
    unsent_trend_ids: set[str] = set()
    trend_picks: list[dict] = []
    if trend_candidates:
        # 긴급 카드로 나간(이번 run + 최근 14일 이력) 사건과 같은 스토리는
        # 제외 — HN front_page(breaking)와 트렌드 검색이 같은 스토리를 각자
        # 잡을 수 있고(id 네임스페이스 분리로 seen으론 안 걸러짐, QA1),
        # 이력 대조가 없으면 다음 run에 새 id로 온 같은 스토리가 다시
        # 샌다(QA3: cross-run 누수)
        already_alerted = urgent_items + [
            {"title": e.get("title", "")} for e in judge.load_history()]
        picks = _select_trend(
            [t for t in trend_candidates
             if not any(dedup_lib.is_similar_event(t, u)
                        for u in already_alerted)],
            config,
        )
        # 발송 여부가 확정될 때까지는 전량 미발송 취급 — 아래 카드뉴스
        # 발행 직후 send_daily_trend가 성공해야만 소진으로 뒤집는다
        unsent_trend_ids = {it["id"] for it in trend_candidates}
        if not _should_send_trend(state, now_kst, run_mode):
            print(
                f"[main] 트렌드 {len(trend_candidates)}건 보류"
                f"(하루 1회 게이트, mode={run_mode}) — 다음 아침 발송",
                file=sys.stderr,
            )
        elif dry_run:
            print(
                f"[main] DRY_RUN: 트렌드 알림 {len(picks)}건 발송 예정 "
                f"(후보 {len(trend_candidates)}건)"
            )
            for it in picks:
                print(f"  - [{it.get('trend_note') or it.get('source')}] "
                      f"{it.get('title')}")
        else:
            trend_picks = picks

    if dry_run:
        print(
            f"[main] DRY_RUN=1 RUN_MODE={run_mode}: 긴급 {len(card_items)}건(개별 카드), "
            f"비긴급 {len(non_urgent_items)}건"
        )
        _print_dry_run_stats(card_items, non_urgent_items)
        if run_mode == "digest":
            print(
                f"[main] DRY_RUN: pending.json 누적 {len(pending)}건 + 이번 비긴급 {len(non_urgent_items)}건 "
                f"= 다이제스트 {len(pending) + len(non_urgent_items)}건 전송 후 pending.json 비움 (기록 생략)"
            )
            _save_preview_cards(
                pending + non_urgent_items, card_items, discord_cfg,
                issue_no=_issue_no(config, now_kst),
                regions=_source_regions(config),
            )
        else:
            existing_ids = {it["id"] for it in pending}
            would_append = [it for it in non_urgent_items if it["id"] not in existing_ids]
            skipped = len(non_urgent_items) - len(would_append)
            print(
                f"[main] DRY_RUN: pending.json에 {len(would_append)}건 추가 예정 "
                f"(중복 {skipped}건 스킵, 기록 생략)"
            )
        for item in card_items + non_urgent_items:
            print(json.dumps(item, ensure_ascii=False, indent=2))
    else:
        had_backlog = False

        if card_items:
            notify.send_cards(card_items, discord_cfg)
            # 발송 성공분만 이력에 — judge가 다음 런에서 같은 사건의
            # 후속 보도를 긴급으로 재판정하지 않게 하는 컨텍스트
            judge.record_history(card_items)
            had_backlog = True

        if run_mode == "digest":
            merged = pending + non_urgent_items
            retained: list[dict] = []  # 소진하지 않고 다음 digest로 이월할 항목
            if merged:
                max_news = config.get("max_news_items", 7)
                max_cve = config.get("max_cve_items", 10)
                news_cap = config.get("librarian_news_cap", 60)
                ttl_days = config.get("pending_ttl_days", 3)

                # v25: 결정적 선별 파이프라인 — 사서(LLM)에게 전 항목을
                # 맡기면 전역 예산(librarian.DEADLINE_SECONDS)을 구조적으로
                # 초과해 뉴스가 무판정 유실된다(2026-07-12: 171건 입력 →
                # 119건 유실 → 뉴스 카드 0장 발행). 사서 입력을 '카드에
                # 실릴 가능성이 있는 소수'로 결정적으로 줄이고, 나머지는
                # 코드가 소진/이월을 책임진다.
                # ① pending TTL: 오래 이월된 무판정 꼬리는 동향 가치가
                #    없다 — 소진(위키·카드 모두 제외)
                fresh, stale_count = _split_fresh(merged, state["seen"], ttl_days)
                if stale_count:
                    print(
                        f"[main] pending TTL {ttl_days}일 초과 {stale_count}건 소진",
                        file=sys.stderr,
                    )
                # ② 논문(dblp 프로시딩 덤프)은 카드 부적합 — 사서 예산만
                #    잠식하므로 digest에서 조용히 소진한다
                paper_count = sum(1 for it in fresh if it.get("category") == "paper")
                if paper_count:
                    print(f"[main] 논문 {paper_count}건 카드 제외(소진)", file=sys.stderr)
                # (trend는 pending에 들어오지 않는다 — 독립 알림 레인.
                #  아래 not in 조건은 과거 state 잔존분 방어)
                news_pool = [
                    it for it in fresh
                    if it.get("category") not in ("paper", "trend")
                    and not cardgen.is_cve_item(it)
                ]
                cve_pool = [
                    it for it in fresh
                    if it.get("category") not in ("paper", "trend")
                    and cardgen.is_cve_item(it)
                ]
                # ③ '오늘의 CVE'는 사서 판정과 무관하게 결정적으로 선발 —
                #    KEV(실악용) 우선, CVSS 내림차순. 미선발 CVE는 소진
                #    (CVE 카드는 그날의 스냅샷이지 적립 대상이 아니다)
                cve_selected = sorted(
                    cve_pool,
                    key=lambda it: (
                        not it.get("kev"),
                        -(it.get("cvss") or 0),
                        -cardgen.heuristic_score(it),
                    ),
                )[:max_cve]
                # ④ 뉴스는 휴리스틱 상위 news_cap건만 사서에 — 초과분은
                #    이월해 다음 digest가 재도전한다(TTL이 무한 누적 청소)
                news_ranked = sorted(
                    news_pool, key=lambda it: -cardgen.heuristic_score(it))
                lib_input = news_ranked[:news_cap] + cve_selected
                retained = news_ranked[news_cap:]
                print(
                    f"[main] digest 선별: 후보 {len(merged)}건 → 사서 입력 "
                    f"{len(lib_input)}건(뉴스 {min(len(news_ranked), news_cap)}"
                    f"+CVE {len(cve_selected)}), 이월 {len(retained)}건",
                    file=sys.stderr,
                )

                # 2nd layer: LLM wiki librarian. Fails open -- any error
                # (missing token, timeout, bad output) returns None and we
                # send a heuristic top-N; a wiki-sync problem must never
                # suppress a real alert.
                # 사서 실행 전에 INDEX 다이어트 — 배치 입력 토큰을 상수로 유지
                _prune_wiki_index(config.get("wiki_index_max_age_days", 60))
                verdict = librarian.run_librarian(lib_input)
                briefing = None
                wiki_new = None
                brief = None

                if verdict is None:
                    print("[main] 위키 사서 실패 — fail-open", file=sys.stderr)
                    # fail-open이어도 카드·링크 상한은 지킨다: 휴리스틱 상위만
                    # 원문으로. 기존 계약대로 전량 소진(발송했으므로 이월 없음)
                    retained = []
                    to_send = news_ranked[:max_news] + cve_selected
                else:
                    action_counts = {"new": 0, "update": 0, "skip_duplicate": 0, "no_wiki": 0}
                    recap_count = 0
                    wiki_worthy = []
                    judged_id_set = set(verdict.get("verdicts", {}).keys())
                    for item in lib_input:
                        if item["id"] not in judged_id_set:
                            # 무판정(예산 소진·청크 실패) — 기본 importance를
                            # 찍으면 백필 자격( judged 여부)과 구분이 안 돼
                            # 뉴스 0장이 재발한다(2026-07-13 NO.7 실측). 건드리지
                            # 않고 이월시킨다.
                            continue
                        item_verdict = verdict["verdicts"][item["id"]]
                        action = item_verdict.get("action")
                        recency = item_verdict.get("recency")
                        # 사서의 한국어 제목·요약 — 카드뉴스에 실린다(요약이 메인).
                        # 누락 시 cardgen이 피드 원문으로 폴백
                        for key in ("title_ko", "summary_ko", "why_ko", "term_ko"):
                            value = item_verdict.get(key)
                            if value:
                                # **볼드**는 summary_ko 전용(카드 라임 강조).
                                # 사서가 제목·용어에 흘리면 렌더러가 문자
                                # 그대로 찍는다(2026-07-23 "**더 젠틀맨**"
                                # 실측) — 병합 시점에 걷어 meta.json까지 보호
                                if key in ("title_ko", "term_ko"):
                                    value = value.replace("**", "")
                                item[key] = value
                        # 사서의 항목별 구체 키워드 — 카드 해시태그·pill이
                        # 규칙 태그(tags) 대신 우선 사용. LLM 출력이라 형태 검증:
                        # 문자열 원소만, 공백 제거, 빈 리스트면 미설정(태그 폴백)
                        tags_ko = item_verdict.get("tags_ko")
                        if isinstance(tags_ko, list):
                            cleaned = [
                                t.strip() for t in tags_ko
                                if isinstance(t, str) and t.strip()
                            ]
                            if cleaned:
                                item["tags_ko"] = cleaned
                        base_importance = item_verdict.get("importance", 3)
                        # LLM 출력 타입 가드 — null·문자열이면 아래 산술·정렬
                        # 키에서 TypeError로 digest 런 전체가 죽는다(QA F1)
                        if not isinstance(base_importance, (int, float)):
                            base_importance = 3
                        penalty = _author_penalty(item, config)
                        item["importance"] = max(1, base_importance - penalty)
                        if penalty:
                            print(
                                f"[main] 작성자 후순위: '{item.get('source')}' "
                                f"{item.get('author','')} importance {base_importance}→{item['importance']}",
                                file=sys.stderr,
                            )
                        if action in action_counts:
                            action_counts[action] += 1
                        # 카드 후보 = 위키에 실린 사건(new/update)만. skip_duplicate·no_wiki
                        # (비사건·중복)는 위키/휴지통에만 남고 카드·링크에서 제외.
                        # 예외: force_digest(수동 재발행) — 같은 날 앞선 발행이
                        # 이미 위키에 적재한 사건을 사서가 전부 skip_duplicate로
                        # 걸러 재발행이 빈 껍데기가 된다(2026-07-13 NO.9 실측:
                        # 오늘 사건 6건 전원 중복 판정 → 뉴스 2장). 재발행의
                        # 목적이 바로 그 사건들의 재게재이므로 카드 후보로
                        # 허용한다(배치 내 중복은 topic·유사도 백스톱이 거른다).
                        if action in ("new", "update") or (
                            force_digest and action == "skip_duplicate"
                        ):
                            # recap = 발행일만 최근이고 알맹이는 지난 사건(재조명·뒤늦은
                            # 재보도). v24: 하드 제외에서 최후순위 백필로 완화(사용자
                            # 결정: 카드뉴스는 웬만하면 표지1+뉴스7+CVE1=9장 유지) —
                            # 신선한 사건만으로 뉴스 7장이 안 차는 날에만 recap이
                            # 남은 슬롯을 채운다. recency 누락은 신선 취급(fail-open)
                            if recency == "recap":
                                recap_count += 1
                                item["_recap"] = True
                            wiki_worthy.append(item)
                    wiki_new = action_counts["new"]
                    print(
                        f"[main] 위키 사서: 신규 {action_counts['new']}건, "
                        f"갱신 {action_counts['update']}건, "
                        f"중복스킵 {action_counts['skip_duplicate']}건, "
                        f"재탕(recap) 후순위 {recap_count}건"
                    )
                    # 사서 예산 소진·청크 실패로 판정 못 받은 뉴스는 이월 —
                    # 다음 digest가 재도전한다(2026-07-12 유실 재발 방지)
                    unjudged_news = [
                        it for it in news_ranked[:news_cap]
                        if it["id"] not in judged_id_set
                    ]
                    if unjudged_news:
                        print(f"[main] 무판정 뉴스 {len(unjudged_news)}건 이월", file=sys.stderr)
                        retained = unjudged_news + retained
                    # v23: 순위 채움(rank-fill) — importance는 컷라인이 아니라
                    # 정렬 기준이다(사용자 결정: 뉴스 7건 상시 보장).
                    # 같은 사건의 교차 소스 보도는 결정적 2중 백스톱으로 차단:
                    # ① 같은 topic slug(사서 출력), ② CVE 교집합·제목 토큰
                    # 유사도(_dedup_similar) — slug가 배치마다 갈려도 막는다
                    news_worthy = [
                        it for it in wiki_worthy if not cardgen.is_cve_item(it)]
                    news_worthy = _dedup_by_topic(
                        news_worthy, verdict.get("verdicts", {}))
                    news_worthy = _dedup_similar(news_worthy)
                    # 정렬 1순위 = 신선/recap 티어(False<True: 신선 먼저) —
                    # recap은 신선한 사건이 상한을 못 채울 때만 뒤에서 채워진다
                    news_sorted = sorted(
                        news_worthy,
                        key=lambda it: (
                            bool(it.get("_recap")),
                            -it.get("importance", 3),
                            -cardgen.heuristic_score(it),
                        ),
                    )
                    to_send_news = news_sorted[:max_news]
                    # 백필: 사서 부분 실패 등으로 뉴스 7장이 안 차면 무판정
                    # 뉴스 상위로 채운다(카드는 원문 제목·요약 폴백) —
                    # 표지1+뉴스7+CVE1=9장 유지가 사용자 결정. 백필분은
                    # 발송되므로 소진(이월 목록에서 제거)한다.
                    to_send_news = _backfill_news(
                        to_send_news, news_ranked, judged_id_set, max_news)
                    # 최종 중복 게이트(3겹의 마지막). 앞선 2겹은 사서 출력에
                    # 의존한다 — topic slug는 무판정 백필분에 아예 없고,
                    # _dedup_similar는 제목 토큰이 갈리면 놓친다(NO.19 중복
                    # 카드). 발송 확정 직전 제목·요약만 LLM 1콜로 재심사하고,
                    # 지운 만큼 슬롯을 다시 채운다. 실패는 fail-open —
                    # 중복 심사가 발행 자체를 막으면 안 된다.
                    groups = librarian.dedup_gate(to_send_news)
                    if groups:
                        gated = _apply_dedup_groups(to_send_news, groups)
                        gate_dropped = (
                            {it["id"] for it in to_send_news}
                            - {it["id"] for it in gated})
                        print(f"[main] 최종 중복 게이트: {len(gate_dropped)}건 제외")
                        to_send_news = _backfill_news(
                            gated, news_ranked, judged_id_set, max_news,
                            excluded_ids=gate_dropped)
                    # 실린 항목은 이월 목록에서 제거(재발송 방지). 게이트가
                    # 지운 무판정 항목은 남겨 다음 digest에서 사서 판정을
                    # 정식으로 받게 한다
                    sent_ids = {it["id"] for it in to_send_news}
                    retained = [it for it in retained if it["id"] not in sent_ids]
                    to_send = to_send_news + cve_selected
                    wiki_only = len(news_worthy) - len(to_send_news)
                    if wiki_only > 0:
                        print(f"[main] 위키 전용 {wiki_only}건 (카드·링크 제외)", file=sys.stderr)
                    # 표지 총평·키워드는 실제 실리는 항목 기준으로 별도 생성(fail-open)
                    brief = librarian.summarize(to_send)
                    if brief:
                        briefing = brief.get("briefing")
                # v20: 텍스트 온리 전환 — og:image·figure(SVG) 단계 폐기(사용자 결정)
                if not to_send:
                    # 카드에 실릴 것이 0건 — 표지+빈 CVE뿐인 껍데기 발행은
                    # 하지 않는다(2026-07-13 실측: 같은 날 연속 재발행으로
                    # 후보 고갈). last_digest_date를 남기지 않으므로 안전망
                    # cron이 후보가 쌓인 뒤 자연 재시도하고, issue_no도
                    # 소모하지 않는다.
                    print(
                        "[main] 카드 후보 0건 — digest 발행 스킵(다음 트리거가 재시도)",
                        file=sys.stderr,
                    )
                else:
                    # stats line on the digest header embed; wiki_new is left
                    # out entirely (not shown as 0) when the librarian failed
                    # open, since "no new wiki topics" and "wiki didn't run"
                    # are different facts
                    stats = {
                        "total": len(to_send),
                        "urgent": len(card_items),
                        "finance": sum(1 for it in to_send if "금융" in (it.get("tags") or [])),
                    }
                    if wiki_new is not None:
                        stats["wiki_new"] = wiki_new
                    # 표지 해시태그: summarize가 뽑은 그날의 키워드, 실패 시 태그 빈도 상위
                    keywords = (brief or {}).get("keywords") or _fallback_keywords(to_send)
                    stats["keywords"] = keywords
                    # 발행 회차(v26): 날짜 기반 — NO. = (KST 오늘 - 기준일) + 1.
                    # 카운터(state issue_no) 방식은 같은 날 재발행마다 번호가
                    # 올라가 사용자 결정으로 폐기: 오늘 몇 번을 발행해도 NO.는
                    # 항상 같다. 기준일은 config issue_epoch(NO.1 발행일).
                    issue_no = _issue_no(config, now_kst)
                    stats["issue_no"] = issue_no
                    # 아침 다이제스트는 카드뉴스 이미지로 전송하고, 렌더/전송
                    # 실패 시에만 기존 텍스트 다이제스트로 fail-open 폴백 —
                    # 어떤 경우에도 아침 브리핑 자체가 사라지면 안 된다
                    try:
                        # 링크 목록은 카드 표시 순서(뉴스→그 외→오늘의 CVE)와
                        # 동일하게 맞춰야 번호가 카드와 1:1로 대응한다
                        top, cve_rest, other_rest = cardgen.plan_cards(to_send)
                        pngs = cardgen.build_cards(
                            to_send,
                            briefing=briefing,
                            stats=stats,
                            colors=discord_cfg.get("colors", {}),
                            regions=_source_regions(config),
                        )
                        link_lines = cardgen.build_link_lines(top, cve_rest, other_rest)
                        # 발송 직전 게이트 — 가이드라인 위반(fatal)이면 카드뉴스를
                        # 보내지 않고 예외를 올려 기존 텍스트 다이제스트 폴백을 태운다
                        fatal, warnings = preflight.check_card_news(
                            pngs, link_lines, to_send, briefing, config)
                        for w in warnings:
                            print(f"[preflight] 경고: {w}", file=sys.stderr)
                        if fatal:
                            for f_msg in fatal:
                                print(f"[preflight] 차단: {f_msg}", file=sys.stderr)
                            raise RuntimeError(
                                f"preflight 실패 {len(fatal)}건 — 카드뉴스 발송 차단")
                        notify.send_card_news(pngs, link_lines)
                        # 발송 성공 확정 후에만 포트폴리오 게시 산출물 저장
                        # (내부에서 모든 실패를 삼킴 — 폴백 이중발송 방지)
                        _publish_trend(
                            pngs, top + other_rest + cve_rest,
                            issue_no=issue_no, briefing=briefing,
                            keywords=stats.get("keywords") or [],
                        )
                        # 인스타/쓰레드 크로스포스트는 collect.yml의 후속
                        # 스텝(crosspost.py)이 담당 — Pages 배포 완료 후
                        # github.io JPEG URL로 발행해야 하기 때문
                    except Exception as exc:
                        print(
                            f"[main] 카드뉴스 렌더 실패 — 텍스트 다이제스트 폴백: {_safe_exc_str(exc)}",
                            file=sys.stderr,
                        )
                        notify.send_digest(to_send, discord_cfg, briefing=briefing, stats=stats)
                    # 발행 성공 확정(카드뉴스·텍스트 폴백 공통 경로)에만 기록 —
                    # 위 이중발행 가드가 이 날짜를 본다
                    state["last_digest_date"] = today_kst
                    had_backlog = True
                    # 트렌드 픽은 아침 브리핑 직후 1회 — 발행이 확정된 이
                    # 지점에서만 나간다(카드뉴스가 안 나간 날은 트렌드도
                    # 없다). 성공해야 후보를 seen으로 소진하고, 실패하면
                    # 미소진으로 남겨 다음 날 아침 재도전한다.
                    if trend_picks and send_daily_trend(
                            trend_picks, discord_cfg, state, today_kst):
                        unsent_trend_ids = set()
            # 이월(retained) = 사서 예산 초과 등으로 판정 못 받은 신선 뉴스만.
            # 그 외(발송분·위키 전용·논문·미선발 CVE·TTL 초과분)는 전부 소진.
            retained_ids = {it["id"] for it in retained}
            save_pending(retained)
            # digest가 소진한 id 마커 — commit step의 merge_state.py가
            # origin pending과 union할 때 이 id들을 부활시키지 않게 한다.
            # (2026-07-12 발견: digest 20분 사이 realtime 커밋이 끼면 union이
            # flush를 매번 무효화해 pending 566건 누적, 사서 예산 초과)
            # 커밋되지 않는 러너 로컬 파일 — 같은 job 안에서만 쓰인다.
            with open(os.path.join(STATE_DIR, ".digest_consumed.json"),
                      "w", encoding="utf-8") as f:
                json.dump(
                    [it["id"] for it in merged if it["id"] not in retained_ids], f)
        else:
            pending_before = len(pending)
            new_pending = append_pending(pending, non_urgent_items)
            if len(new_pending) != pending_before:
                had_backlog = True
            save_pending(new_pending)

        if not had_backlog:
            print("[main] no new items to notify", file=sys.stderr)

    now_iso = datetime.now(timezone.utc).isoformat()
    for item in new_items:
        # 보류된 트렌드는 seen에 남기지 않는다 — 다음 run이 같은 항목을
        # 다시 가져와 스로틀 해제 시점에 발송할 수 있게(대기열 대체 설계)
        if item["id"] in unsent_trend_ids:
            continue
        state["seen"][item["id"]] = now_iso
    state["seen"] = prune_seen(state["seen"])
    dedup_lib.prune_dedup_state(state)
    state["last_run"] = now_iso

    if not dry_run:
        save_state(state)
    else:
        print("[main] DRY_RUN=1: not persisting state/seen.json or state/pending.json")


if __name__ == "__main__":
    main()
