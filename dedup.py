"""1st-layer heuristic cross-source duplicate detection.

main.dedup() (id-based) only catches a literal re-fetch of the same URL/CVE
id. This module catches the same *event* being reported a second time by a
different outlet -- e.g. NVD's own CVE-2026-XXXXX entry followed a day later
by a news site's "OO사, XX 취약점 패치" article about the same CVE, or two
news sites covering the same breach with different headlines and no CVE at
all.

State lives in state/seen.json alongside the existing "seen"/"last_run"
fields (see ensure_dedup_state for backward compatibility with older
seen.json files that don't have these keys yet):

  "alerted_cves":  {CVE_ID: first_alert_iso}   -- pruned after 90 days
  "recent_titles": [{"t": normalized_title, "d": iso}]  -- pruned after 7 days
"""
import re
from datetime import datetime, timedelta, timezone

CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
_TOKEN_RE = re.compile(r"[a-z0-9가-힣]+")

ALERTED_CVE_TTL_DAYS = 90
RECENT_TITLE_TTL_DAYS = 7
TITLE_JACCARD_THRESHOLD = 0.6


def extract_cves(text: str) -> set[str]:
    if not text:
        return set()
    return {m.group(0).upper() for m in CVE_RE.finditer(text)}


def _normalize_title(title: str) -> str:
    # lowercase, keep only alphanumerics + hangul, tokenize -- this throws
    # away punctuation/particles differences between two outlets' headlines
    # about the same story so the jaccard comparison isn't thrown off by
    # e.g. one using a colon and the other a dash
    return " ".join(_TOKEN_RE.findall(title.lower()))


def _item_cves(item: dict) -> set[str]:
    text = f"{item.get('title', '')} {item.get('summary', '')}"
    return extract_cves(text)


def ensure_dedup_state(state: dict) -> None:
    """Mutate state in place so a seen.json written before this feature
    existed gets the new keys instead of KeyError'ing downstream."""
    state.setdefault("alerted_cves", {})
    state.setdefault("recent_titles", [])


def is_cross_duplicate(item: dict, state: dict) -> bool:
    ensure_dedup_state(state)
    cves = _item_cves(item)

    if cves:
        # only a duplicate if EVERY CVE mentioned has already been alerted;
        # an item that adds even one new CVE to the conversation is new news
        return cves.issubset(state["alerted_cves"].keys())

    normalized = _normalize_title(item.get("title", ""))
    tokens = set(normalized.split())
    if not tokens:
        return False

    cutoff = datetime.now(timezone.utc) - timedelta(days=RECENT_TITLE_TTL_DAYS)
    for entry in state["recent_titles"]:
        try:
            entry_dt = datetime.fromisoformat(entry["d"])
        except (KeyError, TypeError, ValueError):
            continue
        if entry_dt < cutoff:
            continue
        other_tokens = set(entry.get("t", "").split())
        if not other_tokens:
            continue
        union = tokens | other_tokens
        if union and len(tokens & other_tokens) / len(union) >= TITLE_JACCARD_THRESHOLD:
            return True
    return False


def record_alerted(item: dict, state: dict, now: datetime = None) -> None:
    """Record an item that passed the cross-duplicate filter (whether it
    ends up as an individual card, in pending.json, or in a digest) so a
    later re-report of the same event is caught even if this one hasn't
    been flushed to Discord yet."""
    ensure_dedup_state(state)
    now = now or datetime.now(timezone.utc)
    now_iso = now.isoformat()

    for cve in _item_cves(item):
        state["alerted_cves"].setdefault(cve, now_iso)

    normalized = _normalize_title(item.get("title", ""))
    if normalized:
        state["recent_titles"].append({"t": normalized, "d": now_iso})


def prune_dedup_state(state: dict, now: datetime = None) -> None:
    ensure_dedup_state(state)
    now = now or datetime.now(timezone.utc)

    cve_cutoff = now - timedelta(days=ALERTED_CVE_TTL_DAYS)
    pruned_cves = {}
    for cve, first_alert in state["alerted_cves"].items():
        try:
            dt = datetime.fromisoformat(first_alert)
        except (TypeError, ValueError):
            continue
        if dt >= cve_cutoff:
            pruned_cves[cve] = first_alert
    state["alerted_cves"] = pruned_cves

    title_cutoff = now - timedelta(days=RECENT_TITLE_TTL_DAYS)
    pruned_titles = []
    for entry in state["recent_titles"]:
        try:
            dt = datetime.fromisoformat(entry.get("d"))
        except (TypeError, ValueError):
            continue
        if dt >= title_cutoff:
            pruned_titles.append(entry)
    state["recent_titles"] = pruned_titles
