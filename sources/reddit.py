"""Reddit 멀티레딧 일간 top (trend source).

수집 경로는 두 겹이다:

① OAuth2 client_credentials(REDDIT_CLIENT_ID/SECRET secret 등록 시).
   무인증 요청은 데이터센터 IP에서 상시 429였다(2026-07-25~08-18 Actions
   실측: 전 run 실패, 브라우저 UA 재시도까지 429). 인증 요청은 클라이언트
   단위 한도를 받아 IP 평판에 좌우되지 않는다. JSON이라 upvote 실점수도
   함께 온다.
② 무인증 RSS 폴백(secret 미등록 또는 OAuth 실패 시). 호스트·UA 조합을
   순서대로 시도한다 — 같은 IP라도 www/old 호스트와 UA에 따라 판정이
   갈린다(2026-08-18 가정용 IP 실측: www+bot-UA 200, www+브라우저 UA 429,
   old+브라우저 UA 200). 어느 경로로 통했는지 로그에 남겨 Actions 환경의
   실제 판정을 다음 튜닝의 근거로 쓴다.

서브레딧별 개별 요청은 rate limit에 걸리므로(기존 'Reddit 보안 커뮤니티'
소스의 교훈) 멀티레딧(r/a+b+c)으로 한 요청에 몰아 받는다. 멀티레딧 top은
절대 점수로 섞여 대형 서브레딧(LocalLLaMA)이 목록을 독식하므로
(2026-07-24 실측: 100건 중 50건) 서브레딧별 상한을 코드에서 건다. 링크는
원문이 아니라 레딧 스레드로 간다 — 토론·맥락이 트렌드 소스의 가치라
HN의 Ask HN 폴백과 같은 결.
"""
import os
import sys
import time
from datetime import datetime, timezone

import feedparser
import requests

from common import _safe_exc_str

# Reddit이 요구하는 UA 형식: <platform>:<app id>:<version> (by /u/<user>)
BOT_UA = "python:sec-feed-bot:1.1 (by /u/yaejida)"

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
OAUTH_URL = "https://oauth.reddit.com/r/{subs}/top?t=day&limit=100&raw_json=1"

# 무인증 폴백 체인 — (호스트, UA, 사전 대기초). 앞에서부터 '진짜 Atom'이
# 올 때까지 시도한다. 200 자체는 성공 신호가 아니다: old.reddit.com은
# 차단 시 200 + HTML 로그인 페이지를 돌려주므로(2026-08-18 실측) 파싱
# 결과에 entry가 있는지까지 봐야 한다.
# www+규격 UA가 주 경로이고, 429는 짧은 간격 재요청에서 주로 났으므로
# (같은 조합이 3분 뒤 재시도에서 429 → 10분 주기 정상 운영에서는 200)
# 같은 조합을 백오프 후 한 번 더 친다.
RSS_FALLBACKS = (
    ("https://www.reddit.com", BOT_UA, 0),
    ("https://www.reddit.com", BOT_UA, 5),
    ("https://old.reddit.com", BOT_UA, 0),
)
RSS_PATH = "/r/{subs}/top/.rss?t=day&limit=100"

BLOCKED_STATUSES = (401, 403, 406, 429, 500, 502, 503)
DEFAULT_PER_SUB = 3


def _oauth_token() -> str | None:
    """client_credentials 토큰 발급. secret 미등록·실패는 None(폴백)."""
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None
    try:
        resp = requests.post(
            TOKEN_URL,
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": BOT_UA},
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception as exc:
        # 토큰 발급 실패가 소스 전체를 죽이면 안 된다 — RSS 폴백으로 계속.
        # 자격증명 자체는 절대 로그에 넣지 않는다(_safe_exc_str이 URL/헤더
        # 노출을 막지 못하는 예외 타입이 있어 메시지도 최소화)
        print(f"[main] Reddit OAuth 토큰 발급 실패(RSS 폴백): "
              f"{_safe_exc_str(exc)}", file=sys.stderr)
        return None


def _fetch_oauth(subs_path: str, token: str) -> list[dict] | None:
    """oauth.reddit.com JSON listing. 실패 시 None(폴백)."""
    try:
        resp = requests.get(
            OAUTH_URL.format(subs=subs_path),
            headers={"Authorization": f"bearer {token}", "User-Agent": BOT_UA},
            timeout=20,
        )
        resp.raise_for_status()
        children = resp.json()["data"]["children"]
    except Exception as exc:
        print(f"[main] Reddit OAuth listing 실패(RSS 폴백): "
              f"{_safe_exc_str(exc)}", file=sys.stderr)
        return None
    print(f"[main] Reddit 트렌드: OAuth 경로 200 ({len(children)}건)")
    return children


def _fetch_rss(subs_path: str):
    """무인증 RSS 폴백 체인. 전부 실패하면 마지막 응답으로 raise."""
    last = None
    for host, ua, backoff in RSS_FALLBACKS:
        if backoff:
            time.sleep(backoff)
        url = host + RSS_PATH.format(subs=subs_path)
        try:
            resp = requests.get(url, timeout=20, headers={"User-Agent": ua})
        except requests.RequestException as exc:
            print(f"[main] Reddit RSS {host} 요청 실패: {_safe_exc_str(exc)}",
                  file=sys.stderr)
            continue
        if resp.status_code in BLOCKED_STATUSES:
            last = resp
            print(f"[main] Reddit RSS {host} {resp.status_code} — 다음 조합 시도",
                  file=sys.stderr)
            continue
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        if not feed.entries:
            # 200 + HTML 차단 페이지(old.reddit.com 실측) — 성공이 아니다.
            # 여기서 멈추면 '200인데 0건'으로 조용히 굶는다
            last = resp
            print(f"[main] Reddit RSS {host} 200이지만 entry 0건"
                  "(차단 페이지 추정) — 다음 조합 시도", file=sys.stderr)
            continue
        print(f"[main] Reddit 트렌드: RSS 경로 200 ({host}, "
              f"entry {len(feed.entries)}건)")
        return feed
    if last is not None and last.status_code in BLOCKED_STATUSES:
        last.raise_for_status()
    raise RuntimeError("Reddit RSS 폴백 전 조합 실패(차단 또는 빈 피드)")


def fetch(source_cfg: dict) -> list[dict]:
    subs = source_cfg.get("subreddits", [])
    if not subs:
        return []
    per_sub = int(source_cfg.get("per_subreddit", DEFAULT_PER_SUB))
    subs_path = "+".join(subs)

    token = _oauth_token()
    if token:
        children = _fetch_oauth(subs_path, token)
        if children is not None:
            return _items_from_json(children, source_cfg, per_sub)

    feed = _fetch_rss(subs_path)

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


def _items_from_json(children: list[dict], source_cfg: dict,
                     per_sub: int) -> list[dict]:
    """OAuth listing(JSON) -> 항목. RSS 경로와 같은 스키마를 낸다.

    RSS와 다른 점은 실제 upvote 수(`score`)가 온다는 것뿐이다. trend_note를
    순위가 아니라 업보트 수로 표기해 '왜 핫한지'의 근거를 강화한다."""
    counts: dict[str, int] = {}
    items = []
    for child in children:
        post = child.get("data") or {}
        post_id = post.get("name") or post.get("id")
        title = post.get("title") or ""
        permalink = post.get("permalink") or ""
        if not post_id or not title or not permalink:
            continue
        # 링크는 레딧 스레드(토론·맥락이 트렌드 소스의 가치). permalink는
        # 레딧이 주는 경로라 스킴 주입 여지가 없지만, 경계에서 형태를 강제
        url = "https://www.reddit.com" + permalink
        if not url.startswith("https://www.reddit.com/"):
            continue
        sub = post.get("subreddit") or "?"
        if counts.get(sub, 0) >= per_sub:
            continue
        counts[sub] = counts.get(sub, 0) + 1
        score = int(post.get("score") or 0)
        items.append({
            "id": f"reddit-{post_id}",
            "source": source_cfg.get("name", "Reddit"),
            "category": source_cfg.get("category", "trend"),
            "title": title,
            "url": url,
            "summary": f"r/{sub} 일간 top",
            "severity": "info",
            "published": _parse_created(post.get("created_utc")),
            "score": score,
            "trend_note": f"r/{sub} ▲{score}",
        })
    return items


def _parse_created(created_utc) -> str:
    try:
        return datetime.fromtimestamp(
            float(created_utc), tz=timezone.utc).isoformat()
    except (TypeError, ValueError):
        return datetime.now(timezone.utc).isoformat()


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
