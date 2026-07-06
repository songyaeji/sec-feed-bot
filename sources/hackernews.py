"""Hacker News front page via Algolia API (breaking-news source).

v8: "클로드 코드 유출"급 대형 사건은 언론 기사보다 HN 프런트페이지에
먼저 뜨는 경우가 많다 — 커뮤니티 업보트가 이미 중요도 필터 역할을
하므로 points 하한만 걸어 가져온다. 이 소스는 config에서 breaking: true
로 표시되어 즉시 발송 판정(judge)에만 쓰이고 아침 다이제스트에는
실리지 않는다 (실제 사건이면 어차피 뉴스 소스로 후속 보도가 온다).
"""
from datetime import datetime, timezone

import requests

API_URL = "https://hn.algolia.com/api/v1/search"
DEFAULT_MIN_POINTS = 150


def fetch(source_cfg: dict) -> list[dict]:
    min_points = source_cfg.get("min_points", DEFAULT_MIN_POINTS)
    resp = requests.get(
        API_URL,
        params={"tags": "front_page", "hitsPerPage": 30},
        timeout=20,
        headers={"User-Agent": "sec-feed-bot/1.0"},
    )
    resp.raise_for_status()
    hits = resp.json().get("hits", [])

    items = []
    for hit in hits:
        object_id = hit.get("objectID")
        title = hit.get("title") or ""
        if not object_id or not title:
            continue
        if (hit.get("points") or 0) < min_points:
            continue
        items.append({
            "id": f"hn-{object_id}",
            "source": source_cfg.get("name", "Hacker News"),
            "category": source_cfg.get("category", "news"),
            "title": title,
            # 원문 링크 우선, 자체 토론(Ask HN 등)이면 HN 스레드로
            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}",
            # HN에는 본문 요약이 없다 — 판정/카드 폴백용으로 지표만 남긴다
            "summary": f"HN {hit.get('points', 0)} points, {hit.get('num_comments', 0)} comments",
            "severity": "info",
            "published": _parse_created(hit),
        })
    return items


def _parse_created(hit) -> str:
    created = hit.get("created_at")
    if created:
        try:
            return datetime.fromisoformat(created.replace("Z", "+00:00")).isoformat()
        except ValueError:
            pass
    return datetime.now(timezone.utc).isoformat()
