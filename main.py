"""Entry point: fetch -> filter -> dedup -> notify -> persist state.

Run by a GitHub Actions cron every 20 minutes. This script only writes
state/seen.json locally; the workflow (not this script) is responsible
for committing that file back to the repo.
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
STATE_DIR = os.path.join(BASE_DIR, "state")
STATE_PATH = os.path.join(STATE_DIR, "seen.json")
PENDING_PATH = os.path.join(STATE_DIR, "pending.json")

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
    # realtime mode calls this every 20 minutes; an id already sitting in
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


def _card_image_sources(config: dict) -> set[str]:
    # 카드에 og:image를 실을 소스. v12: opt-in → opt-out — 품질 게이트
    # (≥600×315, fail-open)가 저품질을 걸러주므로 기본 켠다. 제외는
    # (a) card_image: false 명시, (b) 구글뉴스 쿼리(링크가 리다이렉트라
    # og:image를 못 얻음 — 요청 낭비 방지)
    return {
        s.get("name") for s in config.get("sources", [])
        if s.get("card_image", True)
        and "news.google.com" not in (s.get("url") or "")
    }


def _source_regions(config: dict) -> dict[str, str]:
    # 카드 국내/해외 pill — config sources[].region ("국내"/"해외").
    # 미지정 소스는 맵에서 빠져 카드에서 표기를 생략한다
    return {
        s.get("name"): s["region"]
        for s in config.get("sources", [])
        if s.get("region")
    }


def _fallback_keywords(items: list[dict], limit: int = 4) -> list[str]:
    # 사서가 keywords를 못 준 날의 표지 해시태그 — 태그 빈도 상위로 대체
    counts: dict[str, int] = {}
    for item in items:
        for tag in item.get("tags") or []:
            counts[tag] = counts.get(tag, 0) + 1
    return [t for t, _ in sorted(counts.items(), key=lambda x: -x[1])[:limit]]


def _save_preview_cards(
    merged: list[dict], card_items: list[dict], discord_cfg: dict,
    issue_no: int | None = None, image_sources: set[str] | None = None,
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
            image_sources=image_sources,
            regions=regions,
        )
        preview_dir = os.path.join(STATE_DIR, "preview")
        os.makedirs(preview_dir, exist_ok=True)
        for i, png in enumerate(pngs, start=1):
            with open(os.path.join(preview_dir, f"card_{i:02d}.png"), "wb") as f:
                f.write(png)
        print(f"[main] DRY_RUN: 카드뉴스 {len(pngs)}장 -> state/preview/ 저장")
    except Exception as exc:
        print(f"[main] DRY_RUN: 카드뉴스 렌더 실패(경고만): {_safe_exc_str(exc)}", file=sys.stderr)


def main() -> None:
    config = load_config()
    state = load_state()

    run_mode = os.environ.get("RUN_MODE", "realtime")
    if run_mode not in ("realtime", "digest"):
        print(f"[main] unknown RUN_MODE '{run_mode}', falling back to 'realtime'", file=sys.stderr)
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
    # 게이트 + haiku). 구 기준(KEV/CVSS≥9/긴급 소스)은 폐기: 그런 항목도
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
                image_sources=_card_image_sources(config),
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
            had_backlog = True

        if run_mode == "digest":
            merged = pending + non_urgent_items
            if merged:
                # 2nd layer: LLM wiki librarian. Fails open -- any error
                # (missing token, timeout, bad output) returns None and we
                # send the full merged list; a wiki-sync problem must never
                # suppress a real alert.
                verdict = librarian.run_librarian(merged)
                briefing = None
                wiki_new = None
                brief = None
                # v16: 뉴스·CVE 상한 분리 — CVE(kev/cvss 구조 항목)가 뉴스
                # 슬롯을 잠식하지 않게 각자 상한까지 담는다
                max_news = config.get("max_news_items", 7)
                max_cve = config.get("max_cve_items", 10)
                min_importance = config.get("digest_min_importance", 4)

                def _cap_split(pool: list[dict], key) -> list[dict]:
                    news = sorted((it for it in pool if not cardgen.is_cve_item(it)), key=key)
                    cves = sorted((it for it in pool if cardgen.is_cve_item(it)), key=key)
                    return news[:max_news] + cves[:max_cve]

                if verdict is None:
                    print("[main] 위키 사서 실패 — fail-open", file=sys.stderr)
                    # fail-open이어도 카드·링크 상한은 지킨다: 휴리스틱 상위만 원문으로
                    to_send = _cap_split(
                        merged, key=lambda it: -cardgen.heuristic_score(it))
                else:
                    action_counts = {"new": 0, "update": 0, "skip_duplicate": 0, "no_wiki": 0}
                    wiki_worthy = []
                    for item in merged:
                        item_verdict = verdict.get("verdicts", {}).get(item["id"], {})
                        action = item_verdict.get("action")
                        # 사서의 한국어 제목·요약 — 카드뉴스에 실린다(요약이 메인).
                        # 누락 시 cardgen이 피드 원문으로 폴백
                        for key in ("title_ko", "summary_ko"):
                            value = item_verdict.get(key)
                            if value:
                                item[key] = value
                        item["importance"] = item_verdict.get("importance", 3)
                        if action in action_counts:
                            action_counts[action] += 1
                        # 카드 후보 = 위키에 실린 사건(new/update)만. skip_duplicate·no_wiki
                        # (비사건·중복)는 위키/휴지통에만 남고 카드·링크에서 제외
                        if action in ("new", "update"):
                            wiki_worthy.append(item)
                    wiki_new = action_counts["new"]
                    print(
                        f"[main] 위키 사서: 신규 {action_counts['new']}건, "
                        f"갱신 {action_counts['update']}건, "
                        f"중복스킵 {action_counts['skip_duplicate']}건"
                    )
                    # 정말 중요한 것만 카드·링크에: importance 게이트 + 상한.
                    # 동점은 휴리스틱 점수(AI>KEV>제로데이>금융)로 가른다
                    eligible = [it for it in wiki_worthy if it["importance"] >= min_importance]
                    if not eligible and wiki_worthy:
                        # 전원이 게이트 미달인 날도 다이제스트는 나가야 한다 — 상위 5건 폴백
                        eligible = sorted(wiki_worthy, key=cardgen.heuristic_score, reverse=True)[:5]
                        print(
                            f"[main] importance {min_importance}+ 없음 — 상위 {len(eligible)}건 폴백",
                            file=sys.stderr,
                        )
                    to_send = _cap_split(
                        eligible,
                        key=lambda it: (-it.get("importance", 3), -cardgen.heuristic_score(it)),
                    )
                    wiki_only = len(wiki_worthy) - len(to_send)
                    if wiki_only > 0:
                        print(f"[main] 위키 전용 {wiki_only}건 (카드·링크 제외)", file=sys.stderr)
                    # 표지 총평·키워드는 실제 실리는 항목 기준으로 별도 생성(fail-open)
                    brief = librarian.summarize(to_send)
                    if brief:
                        briefing = brief.get("briefing")
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
                        image_sources=_card_image_sources(config),
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
                except Exception as exc:
                    print(
                        f"[main] 카드뉴스 렌더 실패 — 텍스트 다이제스트 폴백: {_safe_exc_str(exc)}",
                        file=sys.stderr,
                    )
                    notify.send_digest(to_send, discord_cfg, briefing=briefing, stats=stats)
                state["issue_no"] = issue_no + 1
                had_backlog = True
            save_pending([])
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
