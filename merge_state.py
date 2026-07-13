"""Data-level union merge of the JSON state files against another git ref.

Two writers touch state/*.json concurrently: the scheduled Action run and any
direct local push. git's line-based rebase can't auto-merge JSON -- it aborts
with a CONFLICT and fails the job (observed on state/seen.json). But every
state file has append-only, union semantics:

  seen.json         seen / alerted_cves : id -> first-seen iso (only grows)
                    recent_titles       : list of {t, d}      (only grows)
                    last_run            : iso                  (moves forward)
  pending.json      list of items keyed by "id"               (union by id)
  urgent_history    list of {date, title, ...}                (union by tuple)

so the merge is deterministic at the data level. The workflow re-parents its
uncommitted changes onto origin/main with `git reset --soft` (no textual
rebase) and then calls this script to fold in whatever the other writer added,
guaranteeing no seen id / pending item from either side is lost.

Usage:
    python merge_state.py <ref>     # e.g. origin/main

Reads the working-tree copy of each state file and the <ref> copy (via
`git show <ref>:<path>`), writes the union back to the working tree. A file
absent on either side is treated as empty, so this is safe before the first
urgent alert (no urgent_history.json yet) and on a fresh clone.
"""
import json
import os
import subprocess
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")

SEEN_PATH = os.path.join(STATE_DIR, "seen.json")
PENDING_PATH = os.path.join(STATE_DIR, "pending.json")
URGENT_PATH = os.path.join(STATE_DIR, "urgent_history.json")


def _load_local(path: str, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def _load_ref(ref: str, rel_path: str, default):
    # `git show <ref>:<path>` prints the blob at that ref; a non-zero exit
    # means the file doesn't exist on that ref (fresh repo / not yet added),
    # which we treat as an empty state rather than an error
    result = subprocess.run(
        ["git", "show", f"{ref}:{rel_path}"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return default
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return default


def _min_iso(a: str, b: str) -> str:
    # keep the EARLIEST timestamp for a shared key -- first-seen semantics
    # drive the TTL prune windows, so the older sighting is the correct one
    try:
        da = datetime.fromisoformat(a)
        db = datetime.fromisoformat(b)
    except (TypeError, ValueError):
        return a or b
    return a if da <= db else b


def _max_iso(a: str, b: str) -> str:
    if not a:
        return b
    if not b:
        return a
    try:
        da = datetime.fromisoformat(a)
        db = datetime.fromisoformat(b)
    except (TypeError, ValueError):
        return a or b
    return a if da >= db else b


def _merge_first_seen(local: dict, remote: dict) -> dict:
    merged = dict(remote)
    for key, iso in local.items():
        if key in merged:
            merged[key] = _min_iso(merged[key], iso)
        else:
            merged[key] = iso
    return merged


def _merge_recent_titles(local: list, remote: list) -> list:
    # dedup on the exact (normalized-title, iso) pair; two runs that both
    # recorded the same headline at the same instant collapse to one entry
    seen = set()
    merged = []
    for entry in list(remote) + list(local):
        if not isinstance(entry, dict):
            continue
        key = (entry.get("t"), entry.get("d"))
        if key in seen:
            continue
        seen.add(key)
        merged.append(entry)
    return merged


def merge_seen(local: dict, remote: dict) -> dict:
    local = local if isinstance(local, dict) else {}
    remote = remote if isinstance(remote, dict) else {}
    merged = {
        "seen": _merge_first_seen(local.get("seen", {}), remote.get("seen", {})),
        "alerted_cves": _merge_first_seen(
            local.get("alerted_cves", {}), remote.get("alerted_cves", {})
        ),
        "recent_titles": _merge_recent_titles(
            local.get("recent_titles", []), remote.get("recent_titles", [])
        ),
    }
    # issue_no(구 digest 카운터)는 v26에서 날짜 기반 회차로 대체돼 더는
    # merge하지 않는다 — 화이트리스트에서 빠지므로 잔존 키는 다음 merge에서
    # 자연 소거된다.
    merged["last_run"] = _max_iso(local.get("last_run"), remote.get("last_run"))
    # digest 이중발행 가드 날짜(main.py) — YYYY-MM-DD라 사전순 max가 곧
    # 날짜 max. 화이트리스트 merge라 여기 안 넣으면 merge마다 유실돼
    # 가드가 무력화된다
    last_digest = max(
        local.get("last_digest_date") or "", remote.get("last_digest_date") or ""
    )
    if last_digest:
        merged["last_digest_date"] = last_digest
    return merged


def _load_consumed() -> set:
    # digest run이 남기는 소진 id 마커(main.py, 커밋 안 됨) — 이 id들은
    # 방금 발행에 쓰였으므로 origin pending에서 부활시키면 안 된다.
    # 마커가 없으면(realtime run) 빈 집합 = 기존 union 그대로.
    # (2026-07-12: union이 digest flush를 무효화해 pending 566건 누적,
    # 사서 예산 초과로 판정 누락 → 카드 빈약의 근본 원인 수정)
    path = os.path.join(STATE_DIR, ".digest_consumed.json")
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        try:
            ids = json.load(f)
        except json.JSONDecodeError:
            return set()
    return {i for i in ids if isinstance(i, str)}


def merge_pending(local: list, remote: list) -> list:
    local = local if isinstance(local, list) else []
    remote = remote if isinstance(remote, list) else []
    consumed = _load_consumed()
    # union by id; keep the LOCAL copy of a shared id (this run's version may
    # carry freshly enriched fields), but preserve items only the other writer
    # queued so nothing waiting for the next digest is dropped. digest가
    # 소진한 id는 예외 — union에서 제외해 flush가 유지되게 한다.
    by_id = {}
    order = []
    for item in list(remote) + list(local):
        if not isinstance(item, dict) or "id" not in item:
            continue
        item_id = item["id"]
        if item_id in consumed:
            continue
        if item_id not in by_id:
            order.append(item_id)
        by_id[item_id] = item  # local (later in the chain) wins on conflict
    return [by_id[i] for i in order]


def merge_urgent(local: list, remote: list) -> list:
    local = local if isinstance(local, list) else []
    remote = remote if isinstance(remote, list) else []
    seen = set()
    merged = []
    for entry in list(remote) + list(local):
        if not isinstance(entry, dict):
            continue
        key = (entry.get("date"), entry.get("title"))
        if key in seen:
            continue
        seen.add(key)
        merged.append(entry)
    return merged


def _write(path, data, sort_keys, ensure_ascii, indent=2, trailing_newline=True):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii)
        if trailing_newline:
            f.write("\n")


def main(ref: str) -> None:
    # seen.json: match main.save_state byte-for-byte (sort_keys=True,
    # ensure_ascii default True -> hangul escaped) so a merge doesn't rewrite
    # the whole file into a different-but-equivalent encoding and blow up the
    # diff / reintroduce a conflict surface
    local_seen = _load_local(SEEN_PATH, {})
    remote_seen = _load_ref(ref, "state/seen.json", {})
    _write(SEEN_PATH, merge_seen(local_seen, remote_seen), sort_keys=True, ensure_ascii=True)

    # pending.json: match main.save_pending (sort_keys=True, ensure_ascii=False
    # so Korean summaries stay human-readable); the list keeps our merge order
    local_pending = _load_local(PENDING_PATH, [])
    remote_pending = _load_ref(ref, "state/pending.json", [])
    _write(
        PENDING_PATH,
        merge_pending(local_pending, remote_pending),
        sort_keys=True,
        ensure_ascii=False,
    )

    # urgent_history.json only exists once the first urgent alert has fired;
    # skip writing it if neither side has one
    local_urgent = _load_local(URGENT_PATH, None)
    remote_urgent = _load_ref(ref, "state/urgent_history.json", None)
    if local_urgent is not None or remote_urgent is not None:
        merged_urgent = merge_urgent(local_urgent or [], remote_urgent or [])
        # match judge.record_history: indent=1, ensure_ascii=False, no
        # sort_keys, and no trailing newline
        _write(
            URGENT_PATH,
            merged_urgent,
            sort_keys=False,
            ensure_ascii=False,
            indent=1,
            trailing_newline=False,
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python merge_state.py <ref>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
