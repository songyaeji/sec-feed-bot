"""Entry point: fetch -> filter -> dedup -> notify -> persist state.

Run by GitHub Actions every ~10 minutes (external cron-job.org trigger
via workflow_dispatch — see docs/external-trigger.md; the */20 cron is a
fallback). This script only writes state/seen.json locally; the workflow
(not this script) is responsible for committing that file back to the
repo.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import yaml

import cardgen
import dedup as dedup_lib
import judge
import librarian
import notify
import preflight
import tagger
from sources import dblp, fsec, fss, hackernews, kev, nvd, rss

# 크로스포스트(인스타/쓰레드)는 선택적 모듈이다. 아직 배포되지 않은
# 환경(crosspost.py 부재)에서도 수집·발송 파이프라인이 import 단계에서
# 죽지 않도록 가드한다 — 모듈이 없으면 발송은 정상 진행하고 크로스포스트
# 단계만 조용히 건너뛴다
try:
    import crosspost
except ImportError:
    crosspost = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
STATE_DIR = os.path.join(BASE_DIR, "state")
STATE_PATH = os.path.join(STATE_DIR, "seen.json")
PENDING_PATH = os.path.join(STATE_DIR, "pending.json")
# 포트폴리오(songyaeji.github.io) Trend 탭 게시 산출물 — collect.yml의
# 후속 스텝이 이 디렉터리를 포트폴리오 repo로 push한다
TREND_DIR = os.path.join(BASE_DIR, "out", "trend")

SEEN_TTL_DAYS = 90

SEVERITY_ORDER = {"critical": 0, "high": 1, "info": 2}

# requests exceptions can embed the request URL (e.g. connection/timeout
# errors), and webhook URLs carry a bearer token in their path, so any
# exception text we print must have that token pattern masked first
WEBHOOK_TOKEN_RE = re.compile(r"webhooks/\d+/[\w-]+")


def _safe_exc_str(exc: Exception) -> str:
    return f"{type(exc).__name__}: {WEBHOOK_TOKEN_RE.sub('webhooks/***', str(exc))}"

FETCHERS = {
    "kev": kev.fetch,
    "nvd": nvd.fetch,
    "rss": rss.fetch,
    "fsec": fsec.fetch,
    "fss": fss.fetch,
    "dblp": dblp.fetch,
    "hn": hackernews.fetch,
}


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {"seen": {}, "last_run": None}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # tolerate the repo's initial placeholder value of `{}`
    if "seen" not in data:
        data = {"seen": {}, "last_run": data.get("last_run")}
    return data


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write("\n")


def load_pending() -> list[dict]:
    if not os.path.exists(PENDING_PATH):
        return []
    with open(PENDING_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []
    return data if isinstance(data, list) else []


def save_pending(pending: list[dict]) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(PENDING_PATH, "w", encoding="utf-8") as f:
        json.dump(pending, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def append_pending(pending: list[dict], new_items: list[dict]) -> list[dict]:
    # realtime mode calls this every ~10 minutes; an id already sitting in
    # pending.json (queued but not yet flushed by a digest run) must not be
    # appended a second time
    existing_ids = {it["id"] for it in pending}
    for item in new_items:
        if item["id"] in existing_ids:
            continue
        pending.append(item)
        existing_ids.add(item["id"])
    return pending


def prune_seen(seen: dict) -> dict:
    # without pruning, seen.json grows forever since every dedup id is
    # kept indefinitely; 90 days is far longer than any re-alert window
    # we care about, so it's safe to drop older entries
    cutoff = datetime.now(timezone.utc) - timedelta(days=SEEN_TTL_DAYS)
    pruned = {}
    for item_id, first_seen in seen.items():
        try:
            seen_dt = datetime.fromisoformat(first_seen)
        except (TypeError, ValueError):
            continue
        if seen_dt >= cutoff:
            pruned[item_id] = first_seen
    return pruned


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


def collect_all(config: dict, state: dict) -> list[dict]:
    all_items = []
    for source_cfg in config.get("sources", []):
        source_type = source_cfg.get("type")
        fetcher = FETCHERS.get(source_type)
        name = source_cfg.get("name", "<unnamed>")

        if fetcher is None:
            print(f"[main] unknown source type '{source_type}' for '{name}', skipping", file=sys.stderr)
            continue

        try:
            if source_type == "nvd":
                items = fetcher(source_cfg, state, config)
            elif source_type in ("rss", "fsec", "fss"):
                items = fetcher(source_cfg, state, config)
            else:
                items = fetcher(source_cfg)
            # v8: 소스 단위 urgent 플래그 폐기 — 즉시 발송은 judge.py
            # (대형 사건 판정)만 결정한다. breaking 소스(HN·레딧)는
            # 판정 전용: 긴급 아니면 다이제스트에도 안 싣고 버린다
            if source_cfg.get("breaking"):
                for item in items:
                    item["breaking"] = True
            print(f"[main] {name}: fetched {len(items)} item(s)", file=sys.stderr)
            all_items.extend(items)
        except Exception as exc:
            # one flaky source (network blip, bad feed URL, etc.) should
            # never take down the whole run; mask potential webhook
            # tokens since some requests exceptions embed the request URL
            print(f"[main] source '{name}' failed: {_safe_exc_str(exc)}", file=sys.stderr)
    return all_items


def max_items_per_run(config: dict) -> int | None:
    # applies only to individual cards (urgent items); the digest embed
    # already caps itself at DIGEST_MAX_LINES per category ("...외 N건"),
    # so it never needs this cap. env wins over config so a workflow can
    # raise/lower the cap without a commit
    env_value = os.environ.get("MAX_ITEMS_PER_RUN")
    if env_value is not None:
        try:
            return int(env_value)
        except ValueError:
            print(f"[main] invalid MAX_ITEMS_PER_RUN '{env_value}', ignoring", file=sys.stderr)
    return config.get("max_items_per_run")


def dedup(items: list[dict], seen: dict) -> list[dict]:
    new_items = []
    for item in items:
        if item["id"] not in seen:
            new_items.append(item)
    return new_items


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


def _save_preview_cards(
    merged: list[dict], card_items: list[dict], discord_cfg: dict,
    issue_no: int | None = None,
    regions: dict[str, str] | None = None,
) -> None:
    # DRY_RUN digest에서도 렌더 경로를 실제로 태워 PNG를 남긴다 —
    # 전송 없이 로컬에서 카드 디자인을 눈으로 검수하기 위한 용도라서
    # 렌더 실패(playwright 미설치 등)는 경고만 하고 run을 깨지 않는다.
    # 사서(librarian)는 DRY_RUN에서 돌지 않으므로 briefing/wiki_new 없음.
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
        kst = timezone(timedelta(hours=9))
        meta = {
            "date": datetime.now(kst).strftime("%Y-%m-%d"),
            "issue_no": issue_no,
            "briefing": briefing,
            "keywords": keywords,
            "links": [
                {
                    # 제목 개행 정리는 build_link_lines와 동일 규칙
                    "n": i,
                    "title": " ".join((it.get("title") or "").split()),
                    "url": it.get("url", ""),
                }
                for i, it in enumerate(ordered_items, start=1)
            ],
            "cards": names,
        }
        with open(os.path.join(TREND_DIR, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"[main] trend 게시 산출물 저장: out/trend ({len(names)}장)")
    except Exception as exc:
        print(f"[main] trend 산출물 저장 실패(무시): {_safe_exc_str(exc)}", file=sys.stderr)


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
    urgent_items = judge.select_urgent(routable_items, config, allow_llm=not dry_run)
    urgent_ids = {it["id"] for it in urgent_items}
    # breaking 소스(HN·레딧)는 즉시 발송 후보로만 쓴다 — 긴급이 아니면
    # 다이제스트에 싣지 않고 버린다 (seen에는 남아 재등장하지 않는다)
    non_urgent_items = [
        it for it in routable_items
        if it["id"] not in urgent_ids and not it.get("breaking")
    ]
    dropped_breaking = len(routable_items) - len(urgent_items) - len(non_urgent_items)
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
                issue_no=state.get("issue_no", 1),
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
                news_pool = [
                    it for it in fresh
                    if it.get("category") != "paper" and not cardgen.is_cve_item(it)
                ]
                cve_pool = [
                    it for it in fresh
                    if it.get("category") != "paper" and cardgen.is_cve_item(it)
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
                        # (비사건·중복)는 위키/휴지통에만 남고 카드·링크에서 제외
                        if action in ("new", "update"):
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
                    if len(to_send_news) < max_news:
                        selected_ids = {it["id"] for it in to_send_news}
                        for cand in news_ranked:
                            if len(to_send_news) >= max_news:
                                break
                            if cand["id"] in selected_ids or cand["id"] in judged_id_set:
                                continue
                            if any(dedup_lib.is_similar_event(cand, s) for s in to_send_news):
                                continue
                            to_send_news.append(cand)
                            selected_ids.add(cand["id"])
                        retained = [
                            it for it in retained if it["id"] not in selected_ids]
                    to_send = to_send_news + cve_selected
                    wiki_only = len(news_worthy) - len(to_send_news)
                    if wiki_only > 0:
                        print(f"[main] 위키 전용 {wiki_only}건 (카드·링크 제외)", file=sys.stderr)
                    # 표지 총평·키워드는 실제 실리는 항목 기준으로 별도 생성(fail-open)
                    brief = librarian.summarize(to_send)
                    if brief:
                        briefing = brief.get("briefing")
                # v20: 텍스트 온리 전환 — og:image·figure(SVG) 단계 폐기(사용자 결정)
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
                # 발행 회차: seen.json에 다음 회차 번호를 들고 다닌다(최초 1).
                # 실제 전송(카드뉴스든 텍스트 폴백이든)에 성공해야 증가 —
                # 전송 예외 시에는 그대로 남아 다음 시도에 같은 번호로 나간다
                issue_no = state.get("issue_no", 1)
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
                    cdn_urls = notify.send_card_news(pngs, link_lines)
                    # 발송 성공 확정 후에만 포트폴리오 게시 산출물 저장
                    # (내부에서 모든 실패를 삼킴 — 폴백 이중발송 방지)
                    _publish_trend(
                        pngs, top + other_rest + cve_rest,
                        issue_no=issue_no, briefing=briefing,
                        keywords=stats.get("keywords") or [],
                    )
                    # 인스타/쓰레드 크로스포스트 — 반드시 자체 try로 격리:
                    # 예외가 바깥 except에 닿으면 텍스트 다이제스트 폴백이
                    # 실행돼 Discord에 이중 발송되기 때문
                    if crosspost is not None:
                        try:
                            crosspost.crosspost_all(
                                cdn_urls,
                                issue_no=issue_no,
                                briefing=briefing,
                                keywords=stats.get("keywords") or [],
                                cfg=config.get("crosspost", {}),
                            )
                        except Exception as exc:
                            print(
                                f"[main] 크로스포스트 실패(무시): {_safe_exc_str(exc)}",
                                file=sys.stderr,
                            )
                except Exception as exc:
                    print(
                        f"[main] 카드뉴스 렌더 실패 — 텍스트 다이제스트 폴백: {_safe_exc_str(exc)}",
                        file=sys.stderr,
                    )
                    notify.send_digest(to_send, discord_cfg, briefing=briefing, stats=stats)
                state["issue_no"] = issue_no + 1
                # 발행 성공 확정(카드뉴스·텍스트 폴백 공통 경로)에만 기록 —
                # 위 이중발행 가드가 이 날짜를 본다
                state["last_digest_date"] = today_kst
                had_backlog = True
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
