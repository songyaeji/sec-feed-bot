"""Hacker News via Algolia API — 두 모드.

① front_page (기본, breaking-news source): v8 — "클로드 코드 유출"급
대형 사건은 언론 기사보다 HN 프런트페이지에 먼저 뜨는 경우가 많다 —
커뮤니티 업보트가 이미 중요도 필터 역할을 하므로 points 하한만 걸어
가져온다. config에서 breaking: true로 표시되어 즉시 발송 판정(judge)에만
쓰이고 아침 다이제스트에는 실리지 않는다.

② 키워드 검색 (config에 queries가 있으면, trend source): AI 툴·MCP·
skills 등 트렌드 글을 키워드 + points 하한으로 좁혀 다이제스트의
'오늘의 트렌드' 링크 섹션에 싣는다. 최근분만 유효하도록 검색 시점
기준 numericFilters created_at 컷을 함께 건다.
"""
from datetime import datetime, timedelta, timezone

import requests

API_URL = "https://hn.algolia.com/api/v1/search"
DEFAULT_MIN_POINTS = 150
DEFAULT_SEARCH_MIN_POINTS = 100
DEFAULT_SEARCH_MAX_AGE_DAYS = 2


def fetch(source_cfg: dict) -> list[dict]:
    if source_cfg.get("queries"):
        return _fetch_search(source_cfg)
    return _fetch_front_page(source_cfg)


def _fetch_search(source_cfg: dict) -> list[dict]:
    min_points = source_cfg.get("min_points", DEFAULT_SEARCH_MIN_POINTS)
    max_age_days = int(
        source_cfg.get("max_age_days", DEFAULT_SEARCH_MAX_AGE_DAYS))
    cutoff_ts = int(
        (datetime.now(timezone.utc) - timedelta(days=max_age_days)).timestamp())

    seen_ids: set[str] = set()  # 쿼리 간 같은 스토리 중복 방지
    items = []
    for query in source_cfg["queries"]:
        resp = requests.get(
            API_URL,
            params={
                "query": query,
                "tags": "story",
                "hitsPerPage": 10,
                "numericFilters":
                    f"points>={min_points},created_at_i>={cutoff_ts}",
            },
            timeout=20,
            headers={"User-Agent": "sec-feed-bot/1.0"},
        )
        resp.raise_for_status()
        for hit in resp.json().get("hits", []):
            object_id = hit.get("objectID")
            title = hit.get("title") or ""
            if not object_id or not title or object_id in seen_ids:
                continue
            seen_ids.add(object_id)
            points = hit.get("points") or 0
            items.append({
                # 트렌드 전용 네임스페이스 — front_page(breaking) 모드와 id를
                # 공유하면 같은 run에서 breaking 복사본이 seen을 기록해 보류된
                # 트렌드의 재수집이 무력화된다(QA1 지적). 같은 스토리의 긴급
                # 카드↔트렌드 이중 노출은 main의 유사도 필터가 막는다
                "id": f"hn-trend-{object_id}",
                "source": source_cfg.get("name", "HN 트렌드"),
                "category": source_cfg.get("category", "trend"),
                "title": title,
                "url": hit.get("url")
                       or f"https://news.ycombinator.com/item?id={object_id}",
                "summary": f"HN {points} points, "
                           f"{hit.get('num_comments', 0)} comments",
                "severity": "info",
                "published": _parse_created(hit),
                # 트렌드 선별 정렬(점수 내림차순)과 화제성 표기에 쓰인다
                "score": points,
                # 이모지 없이 점수만 — 본문 유형 이모지와 겹치면 지저분하다
                "trend_note": f"HN ▲{points}",
            })
    return items


def _fetch_front_page(source_cfg: dict) -> list[dict]:
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
