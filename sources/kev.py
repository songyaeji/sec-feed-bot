"""CISA Known Exploited Vulnerabilities (KEV) source.

KEV entries are all actively-exploited CVEs by definition, so every
item is treated as "critical" severity regardless of CVSS score.
"""
import requests


def fetch(source_cfg: dict) -> list[dict]:
    url = source_cfg.get("url")
    if not url:
        raise ValueError(f"kev source '{source_cfg.get('name', '<unnamed>')}' is missing required 'url' config")
    category = source_cfg.get("category", "critical")

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for vuln in data.get("vulnerabilities", []):
        cve_id = vuln.get("cveID")
        if not cve_id:
            continue

        vendor = vuln.get("vendorProject", "")
        product = vuln.get("product", "")
        name = vuln.get("vulnerabilityName", cve_id)
        summary = vuln.get("shortDescription", "")

        items.append({
            "id": cve_id,
            "source": source_cfg.get("name", "CISA KEV"),
            "category": category,
            "title": f"{cve_id}: {name} ({vendor} {product})".strip(),
            "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
            "summary": summary[:300],
            "severity": "critical",
            # every KEV entry is, by definition, exploited in the wild;
            # notify.py uses this flag to add a warning line
            "kev": True,
            # dateAdded is when CISA added it to KEV, closest thing to a
            # "published" timestamp this feed offers
            "published": _to_iso(vuln.get("dateAdded")),
        })
    return items


def _to_iso(date_str):
    if not date_str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    # KEV dateAdded is YYYY-MM-DD; normalize to a full ISO timestamp
    return f"{date_str}T00:00:00+00:00"
