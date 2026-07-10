"""NVD API 2.0 source with CVSS/keyword filtering.

Only pulls CVEs modified since the last successful run, then keeps
the ones that look either severe (CVSS) or relevant (keyword hit).
"""
import os
import time
from datetime import datetime, timedelta, timezone

import requests

API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
RESULTS_PER_PAGE = 2000


def fetch(source_cfg: dict, state: dict, global_cfg: dict) -> list[dict]:
    url = source_cfg.get("url", API_BASE)
    category = source_cfg.get("category", "high")

    filt = global_cfg.get("nvd_filter", {})
    min_cvss = source_cfg.get("min_cvss", filt.get("min_cvss", 8.0))
    keywords = [k.lower() for k in source_cfg.get("keywords", filt.get("keywords", []))]

    last_run = state.get("last_run")
    if last_run:
        start = last_run
    else:
        # first run ever: no baseline, so just look back 24h instead of
        # pulling the entire NVD history
        start = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    api_key = os.environ.get("NVD_API_KEY")
    headers = {"apiKey": api_key} if api_key else {}

    items = []
    start_index = 0
    while True:
        params = {
            "lastModStartDate": start,
            "lastModEndDate": datetime.now(timezone.utc).isoformat(),
            "resultsPerPage": RESULTS_PER_PAGE,
            "startIndex": start_index,
        }
        resp = requests.get(API_BASE, params=params, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        for vuln in data.get("vulnerabilities", []):
            cve = vuln.get("cve", {})
            item = _to_item(cve, category, min_cvss, keywords, source_cfg)
            if item:
                items.append(item)

        total_results = data.get("totalResults", 0)
        start_index += RESULTS_PER_PAGE
        if start_index >= total_results:
            break

        # NVD's public rate limit (no API key) is far stricter than the
        # keyed limit, so we throttle between pages to avoid 403/429s
        if not api_key:
            time.sleep(6)

    return items


def _to_item(cve: dict, category: str, min_cvss: float, keywords: list[str], source_cfg: dict):
    cve_id = cve.get("id")
    if not cve_id:
        return None

    descriptions = cve.get("descriptions", [])
    desc_text = next((d["value"] for d in descriptions if d.get("lang") == "en"), "")

    score = _extract_cvss(cve)
    keyword_hit = any(kw in desc_text.lower() for kw in keywords)

    if score is None and not keyword_hit:
        return None
    if score is not None and score < min_cvss and not keyword_hit:
        return None

    severity = "critical" if (score is not None and score >= 9.0) else "high"

    return {
        "id": cve_id,
        "source": source_cfg.get("name", "NVD"),
        "category": category,
        "title": f"{cve_id} (CVSS {score if score is not None else 'N/A'})",
        "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
        # 1500자: rss.py와 동일 — 300자 절단은 사서 요약의 정보 밀도를 깎는다
        "summary": desc_text[:1500],
        "severity": severity,
        "cvss": score,
        "published": cve.get("published", datetime.now(timezone.utc).isoformat()),
    }


def _extract_cvss(cve: dict):
    metrics = cve.get("metrics", {})
    for key in ("cvssMetricV31", "cvssMetricV30"):
        entries = metrics.get(key)
        if entries:
            return entries[0]["cvssData"]["baseScore"]
    return None
