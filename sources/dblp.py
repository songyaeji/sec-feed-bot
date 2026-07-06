"""dblp top-tier security conference paper source.

dblp's public search API returns transient 500s fairly often under
back-to-back requests, so each stream request is throttled (6s between
streams) and retried (10s backoff, up to 2 retries) before that stream is
given up on; one bad stream must not block the others.

Results come back year-descending, so this only needs to keep the current
and previous year to skip the (often large) historical backlog.
"""
import sys
import time
from datetime import datetime, timezone

import requests

API_BASE = "https://dblp.org/search/publ/api"
REQUEST_DELAY = 6
RETRY_DELAY = 10
MAX_RETRIES = 2
HEADERS = {"User-Agent": "sec-feed-bot/1.0"}


def fetch(source_cfg: dict) -> list[dict]:
    streams = source_cfg.get("streams", {})
    category = source_cfg.get("category", "paper")
    source_name = source_cfg.get("name", "dblp")

    current_year = datetime.now(timezone.utc).year
    allowed_years = {current_year, current_year - 1}

    items = []
    stream_list = list(streams.items())
    for idx, (stream_key, display_name) in enumerate(stream_list):
        try:
            hits = _fetch_stream(stream_key)
        except Exception as exc:
            print(f"[dblp] stream '{stream_key}' failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            hits = []

        for hit in hits:
            item = _to_item(hit, display_name, category, source_name, allowed_years)
            if item:
                items.append(item)

        # keep dblp happy between streams; skip the trailing sleep after
        # the last one since nothing follows it
        if idx < len(stream_list) - 1:
            time.sleep(REQUEST_DELAY)

    return items


def _fetch_stream(stream_key: str) -> list[dict]:
    params = {
        "q": f"stream:streams/conf/{stream_key}:",
        "h": 30,
        "format": "json",
    }

    attempt = 0
    while True:
        try:
            resp = requests.get(API_BASE, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get("result", {}).get("hits", {}).get("hit", []) or []
        except (requests.RequestException, ValueError):
            attempt += 1
            if attempt > MAX_RETRIES:
                raise
            time.sleep(RETRY_DELAY)


def _to_item(hit: dict, display_name: str, category: str, source_name: str, allowed_years: set):
    info = hit.get("info", {})

    try:
        year = int(info.get("year"))
    except (TypeError, ValueError):
        return None
    if year not in allowed_years:
        return None

    key = info.get("key")
    title = info.get("title", "")
    if not key or not title:
        return None

    ee = info.get("ee")
    if isinstance(ee, list):
        ee = ee[0] if ee else None
    url = ee or info.get("url") or f"https://dblp.org/rec/{key}"

    return {
        "id": key,
        "source": source_name,
        "category": category,
        "title": f"[{display_name} {year}] {title}",
        "url": url,
        "summary": "",
        "severity": "info",
        "published": f"{year}-01-01T00:00:00+00:00",
    }
