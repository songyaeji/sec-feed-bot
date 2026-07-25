"""Reddit 멀티레딧 일간 top RSS (trend source).

JSON API(top.json)는 봇·브라우저 UA 모두 403(2026-07-24 실측: www·old
공통 차단)이라 RSS(Atom)로 간다. 서브레딧별 개별 요청은 레딧 rate
limit(429)에 걸리므로(기존 'Reddit 보안 커뮤니티' 소스의 교훈) 멀티레딧
(r/a+b+c)으로 한 요청에 몰아 받는다.

RSS에는 upvote 점수가 없지만 top?t=day 정렬 자체가 업보트 순위이므로
피드 순서 = 화제성 순위로 쓴다. 멀티레딧 top은 절대 점수로 섞여 대형
서브레딧(LocalLLaMA)이 목록을 독식하므로(2026-07-24 실측: 100건 중 50건)
서브레딧별 상한을 코드에서 건다. 링크는 원문이 아니라 레딧 스레드로
간다 — 토론·맥락이 트렌드 소스의 가치라 HN의 Ask HN 폴백과 같은 결.
"""
from datetime import datetime, timezone

import feedparser
import requests

from sources.rss import _BROWSER_UA

FEED_URL = "https://www.reddit.com/r/{subs}/top/.rss?t=day&limit=100"
DEFAULT_PER_SUB = 3


def fetch(source_cfg: dict) -> list[dict]:
    subs = source_cfg.get("subreddits", [])
    if not subs:
        return []
    per_sub = int(source_cfg.get("per_subreddit", DEFAULT_PER_SUB))

    url = FEED_URL.format(subs="+".join(subs))
    resp = requests.get(url, timeout=20, headers={"User-Agent": "sec-feed-bot/1.0"})
    if resp.status_code in (403, 406, 429):
        # 레딧이 데이터센터 IP + 봇 UA 조합을 429로 상시 차단(2026-07-25
        # Actions 실측: 25/25 run 실패) — rss.py와 같은 브라우저 UA 1회
        # 재시도. 정상 응답이면 이 분기를 안 탄다.
        resp = requests.get(url, timeout=20, headers={"User-Agent": _BROWSER_UA})
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)

    counts: dict[str, int] = {}
    items = []
    for rank, entry in enumerate(feed.entries):  # 피드 순서 = top?t=day 업보트 순위
        entry_id = entry.get("id") or entry.get("link")
        title = entry.get("title", "")
        link = str(entry.get("link", ""))
        if not entry_id or not title:
            continue
        if not link.startswith(("http://", "https://")):
            # 비 http(s) 스킴은 meta.json 경유로 노출될 수 있어 경계에서 드롭
            continue
        sub = _entry_subreddit(entry)
        if counts.get(sub, 0) >= per_sub:
            continue
        counts[sub] = counts.get(sub, 0) + 1
        items.append({
            "id": f"reddit-{entry_id}",
            "source": source_cfg.get("name", "Reddit"),
            "category": source_cfg.get("category", "trend"),
            "title": title,
            "url": link,
            # RSS 본문은 HTML 보일러플레이트(submitted by …)뿐 — 요약 무의미
            "summary": f"r/{sub} 일간 top",
            "severity": "info",
            "published": _parse_published(entry),
            # 점수 대용 = 피드 순위 역순 — _select_trend의 소스 내 정렬용
            # (RSS라 실제 upvote 수는 없다)
            "score": len(feed.entries) - rank,
            # 화제성 표기 — "왜 핫한지"의 결정적 근거(RSS라 점수는 없어
            # 서브레딧 내 일간 순위로 보여준다)
            "trend_note": f"r/{sub} 일간 {counts[sub]}위",
        })
    return items


def _entry_subreddit(entry) -> str:
    # 멀티레딧 Atom entry의 <category term="netsec" label="r/netsec"/>
    tags = entry.get("tags") or []
    if tags and tags[0].get("term"):
        return tags[0]["term"]
    return "?"


def _parse_published(entry) -> str:
    for key in ("published", "updated"):
        raw = entry.get(key)
        if raw:
            try:
                return datetime.fromisoformat(
                    str(raw).replace("Z", "+00:00")).isoformat()
            except ValueError:
                pass
    return datetime.now(timezone.utc).isoformat()
