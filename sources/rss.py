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
    # 신선도 게이트: 소스에 max_age_days가 있으면 그 값이 우선, 없으면 전역
    # default_max_age_days를 쓴다(오래된 재게시·역주행 원문 차단). false/0/None은
    # 필터 해제 — 릴리스/논문 atom처럼 오래돼도 유효한 피드용 탈출구.
    if "max_age_days" in source_cfg:
        max_age_days = source_cfg["max_age_days"]
    else:
        max_age_days = (global_cfg or {}).get("default_max_age_days")

    cutoff = None
    if max_age_days:  # None, False, 0 → 필터 없음
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
            # 바이라인(예: "[지진솔기자 (email)]") — deprioritize_authors 매칭용.
            # 피드에 없으면 빈 문자열
            "author": entry.get("author", "") or "",
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
