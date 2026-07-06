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
import librarian
import notify
import tagger
from sources import dblp, kev, nvd, rss

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
    "dblp": dblp.fetch,
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
            elif source_type == "rss":
                items = fetcher(source_cfg, state, config)
            else:
                items = fetcher(source_cfg)
            if source_cfg.get("urgent"):
                for item in items:
                    item["urgent_source"] = True
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


def is_urgent(item: dict) -> bool:
    # urgent := source is flagged urgent in config.yaml (stamped onto the
    # item as "urgent_source" in collect_all), or CVSS >= 9.0, or a
    # known-exploited (KEV) flag -- any one of these skips the digest queue
    # and goes out as an individual card immediately
    if item.get("urgent_source"):
        return True
    cvss = item.get("cvss")
    if cvss is not None and cvss >= 9.0:
        return True
    if item.get("kev") is True:
        return True
    return False


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


def _save_preview_cards(merged: list[dict], card_items: list[dict], discord_cfg: dict) -> None:
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
        pngs = cardgen.build_cards(
            merged, briefing=None, stats=stats, colors=discord_cfg.get("colors", {})
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

    urgent_items = [it for it in routable_items if is_urgent(it)]
    non_urgent_items = [it for it in routable_items if not is_urgent(it)]

    # cap what we send as individual cards, but still mark everything as
    # seen below so the overflow is not re-sent on the next run
    card_items = urgent_items
    cap = max_items_per_run(config)
    if cap is not None and len(urgent_items) > cap:
        card_items = urgent_items[:cap]
        print(f"{len(urgent_items) - cap}건 생략(개별 카드 상한 초과)")

    pending = load_pending()
    discord_cfg = config.get("discord", {})
    dry_run = os.environ.get("DRY_RUN") == "1"

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
            _save_preview_cards(pending + non_urgent_items, card_items, discord_cfg)
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
                if verdict is None:
                    print("[main] 위키 사서 실패 — fail-open", file=sys.stderr)
                    to_send = merged
                else:
                    briefing = verdict.get("briefing")
                    action_counts = {"new": 0, "update": 0, "skip_duplicate": 0, "no_wiki": 0}
                    to_send = []
                    for item in merged:
                        action = verdict.get("verdicts", {}).get(item["id"], {}).get("action")
                        if action in action_counts:
                            action_counts[action] += 1
                        if action == "skip_duplicate":
                            continue
                        to_send.append(item)
                    wiki_new = action_counts["new"]
                    print(
                        f"[main] 위키 사서: 신규 {action_counts['new']}건, "
                        f"갱신 {action_counts['update']}건, "
                        f"중복스킵 {action_counts['skip_duplicate']}건"
                    )
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
                # 아침 다이제스트는 카드뉴스 이미지로 전송하고, 렌더/전송
                # 실패 시에만 기존 텍스트 다이제스트로 fail-open 폴백 —
                # 어떤 경우에도 아침 브리핑 자체가 사라지면 안 된다
                try:
                    top = cardgen.pick_top(to_send)
                    top_ids = {it["id"] for it in top}
                    rest = [it for it in to_send if it["id"] not in top_ids]
                    pngs = cardgen.build_cards(
                        to_send,
                        briefing=briefing,
                        stats=stats,
                        colors=discord_cfg.get("colors", {}),
                    )
                    notify.send_card_news(pngs, cardgen.build_link_lines(top, rest))
                except Exception as exc:
                    print(
                        f"[main] 카드뉴스 렌더 실패 — 텍스트 다이제스트 폴백: {_safe_exc_str(exc)}",
                        file=sys.stderr,
                    )
                    notify.send_digest(to_send, discord_cfg, briefing=briefing, stats=stats)
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
