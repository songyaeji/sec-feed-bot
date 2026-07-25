"""state/seen.json·pending.json·config.yaml 읽기/쓰기.

JSON 덤프 인자(indent=2, sort_keys=True 등)는 merge_state.py가 byte 단위로
재현하므로 바꾸면 안 된다.
"""
import json
import os
from datetime import datetime, timedelta, timezone

import yaml

from common import CONFIG_PATH, PENDING_PATH, SEEN_TTL_DAYS, STATE_DIR, STATE_PATH


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
