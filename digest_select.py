"""digest 카드 선별 로직 — 중복 제거 3겹 중 결정적 2겹(_dedup_by_topic,
_dedup_similar)·신선도(_split_fresh)·감점(_author_penalty)·회차(_issue_no)."""
import sys
from datetime import datetime, timedelta, timezone

import cardgen
import dedup as dedup_lib


def _author_penalty(item: dict, config: dict) -> int:
    # deprioritize_authors 규칙에 걸리는 바이라인이면 importance 감점폭을 돌려준다.
    # 여러 규칙에 걸리면 가장 큰 penalty만 적용(중복 감점 안 함)
    author = item.get("author") or ""
    source = item.get("source") or ""
    pen = 0
    for rule in config.get("deprioritize_authors", []):
        rule_source = rule.get("source")
        if rule_source and rule_source != source:
            continue
        needle = rule.get("author_contains")
        if needle and needle in author:
            pen = max(pen, int(rule.get("penalty", 1)))
    return pen


def _source_regions(config: dict) -> dict[str, str]:
    # 카드 국내/해외 pill — config sources[].region ("국내"/"해외").
    # 미지정 소스는 맵에서 빠져 카드에서 표기를 생략한다
    return {
        s.get("name"): s["region"]
        for s in config.get("sources", [])
        if s.get("region")
    }


def _dedup_by_topic(items: list[dict], verdicts: dict) -> list[dict]:
    """같은 위키 토픽(slug)에 매인 카드 후보가 2건 이상이면 1건만 남긴다.

    사서 LLM이 같은 사건의 교차 소스 보도를 skip_duplicate로 못 걸러도
    (GodDamn/PoisonX 2026-07-10 사례: THN·Security Affairs 각각 new/update
    판정 → 카드 2장) topic slug는 같게 주므로, 여기서 결정적으로 차단한다.
    생존자는 카드 정렬 기준과 동일한 (-importance, -heuristic_score) 우선.
    slug가 유효한 문자열이 아니면(null/누락) 판단 근거가 없으므로 그대로
    통과시킨다 — 사서 출력 불량이 카드를 지우면 안 된다(fail-open)."""
    best_by_topic: dict[str, dict] = {}
    dup_counts: dict[str, int] = {}
    for item in items:
        topic = verdicts.get(item["id"], {}).get("topic")
        if not (isinstance(topic, str) and topic.strip()):
            continue
        topic = topic.strip()
        current = best_by_topic.get(topic)
        if current is None:
            best_by_topic[topic] = item
            continue
        dup_counts[topic] = dup_counts.get(topic, 0) + 1
        challenger_key = (-item.get("importance", 3), -cardgen.heuristic_score(item))
        current_key = (-current.get("importance", 3), -cardgen.heuristic_score(current))
        if challenger_key < current_key:
            best_by_topic[topic] = item

    for topic, count in dup_counts.items():
        print(
            f"[main] 같은 토픽 카드 중복 {count}건 제외 (topic={topic})",
            file=sys.stderr,
        )

    winners = {id(it) for it in best_by_topic.values()}

    def _keep(item: dict) -> bool:
        topic = verdicts.get(item["id"], {}).get("topic")
        if not (isinstance(topic, str) and topic.strip()):
            return True  # topic 없음 — fail-open 통과
        return id(item) in winners

    return [it for it in items if _keep(it)]


def _split_fresh(items: list[dict], seen: dict, ttl_days: int) -> tuple[list[dict], int]:
    """pending TTL — seen 최초 목격이 ttl_days보다 오래된 항목을 걸러낸다.
    카드뉴스는 일간 동향이라 며칠씩 이월된 무판정 꼬리는 카드 가치가 없고,
    이월 무한 누적(사서 예산 재초과 → 뉴스 유실 재발)의 원인이 된다.
    이번 run에서 처음 본 항목은 seen에 아직 없다 — 신선 취급."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=ttl_days)
    fresh: list[dict] = []
    stale = 0
    for item in items:
        first_seen = seen.get(item.get("id"))
        if first_seen:
            try:
                if datetime.fromisoformat(first_seen) < cutoff:
                    stale += 1
                    continue
            except (TypeError, ValueError):
                pass
        fresh.append(item)
    return fresh, stale


def _dedup_similar(items: list[dict]) -> list[dict]:
    """결정적 유사 사건 dedup — CVE 교집합 또는 제목(원문·한국어) 토큰
    유사도로 같은 사건의 교차 소스 보도를 걸러낸다. topic slug 백스톱
    (_dedup_by_topic)은 사서가 두 배치에서 다른 slug를 주면 뚫린다
    (2026-07 사용자 보고: 같은 내용 카드 2장) — slug와 무관한 최종
    방어선. 중요도 상위가 생존한다."""
    kept: list[dict] = []
    for item in sorted(
        items,
        key=lambda it: (-(it.get("importance") or 0), -cardgen.heuristic_score(it)),
    ):
        dup = next((k for k in kept if dedup_lib.is_similar_event(item, k)), None)
        if dup is not None:
            print(
                f"[main] 유사 사건 카드 중복 제외: {item.get('title_ko') or item.get('title')} "
                f"(대표: {dup.get('title_ko') or dup.get('title')})",
                file=sys.stderr,
            )
            continue
        kept.append(item)
    return kept


def _fallback_keywords(items: list[dict], limit: int = 4) -> list[str]:
    # 사서가 keywords를 못 준 날의 표지 해시태그 — 태그 빈도 상위로 대체
    counts: dict[str, int] = {}
    for item in items:
        for tag in item.get("tags") or []:
            counts[tag] = counts.get(tag, 0) + 1
    return [t for t, _ in sorted(counts.items(), key=lambda x: -x[1])[:limit]]


# 날짜 기반 회차의 기본 기준일 — NO.1 = 2026-07-08, NO.5 = 07-12, NO.6 = 07-13.
# config issue_epoch("YYYY-MM-DD")로 조정 가능.
DEFAULT_ISSUE_EPOCH = "2026-07-08"


def _issue_no(config: dict, now_kst: datetime) -> int:
    """발행 회차 = (KST 오늘 - 기준일) + 1. 날짜의 순수 함수라 같은 날
    몇 번을 재발행해도 항상 같은 번호가 나온다(사용자 결정 — 구 카운터
    방식은 재발행마다 번호를 소모했다). 기준일 파싱 실패는 기본값 폴백."""
    raw = str(config.get("issue_epoch") or DEFAULT_ISSUE_EPOCH)
    try:
        epoch = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        epoch = datetime.strptime(DEFAULT_ISSUE_EPOCH, "%Y-%m-%d").date()
    return (now_kst.date() - epoch).days + 1


def _backfill_news(to_send_news: list[dict], news_ranked: list[dict],
                   judged_id_set: set, max_news: int,
                   excluded_ids: frozenset | set = frozenset()) -> list[dict]:
    """뉴스 상한이 안 차면 무판정 뉴스 상위로 채운 **새 리스트**를 돌려준다.

    사서 부분 실패·중복 게이트 삭제로 슬롯이 비는 두 경로에서 공용으로
    쓴다. 표지1+뉴스7+CVE1=9장 유지가 사용자 결정.
    excluded_ids: 이번 발행에서 이미 탈락한 항목(게이트가 지운 중복) —
    다시 채우면 게이트가 무의미해진다."""
    filled = list(to_send_news)
    selected_ids = {it["id"] for it in filled}
    for cand in news_ranked:
        if len(filled) >= max_news:
            break
        if cand["id"] in selected_ids or cand["id"] in judged_id_set:
            continue
        if cand["id"] in excluded_ids:
            continue
        if any(dedup_lib.is_similar_event(cand, s) for s in filled):
            continue
        # 백필은 사서 요약 없이 원문 폴백으로 실린다 — 피드 요약이 제목과
        # 동일한 껍데기(구글뉴스류)는 '제목=본문' 카드가 되므로 제외
        # (2026-07-24 NO.17 실측 2장). 해당 항목은 이월돼 다음 digest에서
        # 사서 판정을 다시 받는다.
        if not cardgen.has_informative_summary(cand):
            continue
        filled.append(cand)
        selected_ids.add(cand["id"])
    return filled


def _apply_dedup_groups(items: list[dict], groups: list[list[int]]) -> list[dict]:
    """중복 게이트가 준 묶음(1-based)에서 대표 1건만 남긴 새 리스트.

    대표 선정은 카드 정렬 기준과 동일한 (-importance, -heuristic_score).
    입력 순서는 보존한다 — 정렬은 이미 끝난 뒤 호출된다."""
    drop: set[int] = set()
    for group in groups:
        winner = min(
            group,
            key=lambda n: (-(items[n - 1].get("importance") or 0),
                           -cardgen.heuristic_score(items[n - 1])),
        )
        for n in group:
            if n == winner:
                continue
            drop.add(n)
            print(
                "[main] 최종 중복 게이트 제외: "
                f"{items[n - 1].get('title_ko') or items[n - 1].get('title')} "
                f"(대표: {items[winner - 1].get('title_ko') or items[winner - 1].get('title')})",
                file=sys.stderr,
            )
    return [it for i, it in enumerate(items, start=1) if i not in drop]
