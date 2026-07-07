"""Generic RSS/Atom source via feedparser."""
import html
import re
from datetime import datetime, timedelta, timezone

import feedparser
import requests

# 일부 피드(HubSpot 블로그 등)는 description에 이미지 래퍼 <div>까지 통째로
# 실어 보낸다. 마크업을 남기면 카드 요약·사서 입력에 태그가 글자로 노출된다.
# strip → unescape → strip 순서: 엔티티로 인코딩된 태그(&lt;div&gt;)까지 걷어낸다.
# `<[^>]*$`: 원문이 잘려 닫는 >가 없는 미완결 태그 꼬리까지 지운다
_TAG_RE = re.compile(r"<[^>]*>|<[^>]*$")


def _strip_html(text: str) -> str:
    text = _TAG_RE.sub(" ", text or "")
    text = _TAG_RE.sub(" ", html.unescape(text))
    return " ".join(text.split())


def fetch(source_cfg: dict, state: dict = None, global_cfg: dict = None) -> list[dict]:
    url = source_cfg["url"]
    category = source_cfg.get("category", "research")
    keywords = [k.lower() for k in source_cfg.get("keywords", [])]
    max_age_days = source_cfg.get("max_age_days")

    # 신규 소스 첫 실행 때 백로그가 통째로 들어오는 것을 막는다.
    # 미설정 소스는 기존 동작 그대로 전건 반환
    cutoff = None
    if max_age_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=int(max_age_days))

    # feedparser.parse(url) has no timeout of its own; fetch via requests
    # first so an unresponsive feed can't hang the Actions job forever
    resp = requests.get(url, timeout=20, headers={"User-Agent": "sec-feed-bot/1.0"})
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)

    items = []
    for entry in feed.entries:
        entry_id = entry.get("id") or entry.get("link")
        if not entry_id:
            continue

        title = entry.get("title", "")
        summary = _strip_html(entry.get("summary", ""))

        if keywords:
            haystack = f"{title} {summary}".lower()
            if not any(kw in haystack for kw in keywords):
                continue

        published = _parse_published(entry)
        if cutoff is not None:
            try:
                if datetime.fromisoformat(published) < cutoff:
                    continue
            except ValueError:
                pass  # 파싱 불가 날짜는 버리지 않고 통과시킨다

        items.append({
            "id": entry_id,
            "source": source_cfg.get("name", url),
            "category": category,
            "title": title,
            "url": entry.get("link", ""),
            "summary": summary[:300],
            "severity": "info",
            "published": published,
        })
    return items


def _parse_published(entry) -> str:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        try:
            return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()
        except (TypeError, ValueError):
            pass
    # malformed/missing date in feed entry; better to timestamp it now
    # than to drop the item entirely
    return datetime.now(timezone.utc).isoformat()
