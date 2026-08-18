"""sources/reddit.py 단위 테스트 — 전 요청 모킹(오프라인 안전).

핵심 검증 두 가지:
① OAuth secret이 있으면 인증 경로를 쓰고 RSS를 아예 안 친다(2026-08-18:
   데이터센터 IP 무인증 요청이 상시 429라 인증이 주 경로가 됐다).
② secret이 없거나 OAuth가 실패하면 RSS 폴백 체인이 호스트·UA 조합을
   차례로 시도한다(2026-07-25 Actions 상시 429 사고의 재발 방지 가드).
"""
import os
from unittest import mock

import requests

from sources import reddit

# 멀티레딧 Atom 최소 표본 — category term = 서브레딧
_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>t3_aaa</id><title>First post</title>
    <link href="https://www.reddit.com/r/netsec/comments/aaa/"/>
    <category term="netsec" label="r/netsec"/>
    <updated>2026-07-25T00:00:00+00:00</updated>
  </entry>
  <entry>
    <id>t3_bbb</id><title>Second post</title>
    <link href="https://www.reddit.com/r/netsec/comments/bbb/"/>
    <category term="netsec" label="r/netsec"/>
    <updated>2026-07-25T01:00:00+00:00</updated>
  </entry>
</feed>"""

_CFG = {"name": "Reddit 트렌드", "subreddits": ["netsec"], "per_subreddit": 1}


def _response(status: int, body: bytes = b"") -> requests.Response:
    resp = requests.Response()
    resp.status_code = status
    resp._content = body
    return resp


def test_429_walks_fallback_chain(monkeypatch):
    """첫 조합이 429면 다음 (호스트, UA) 조합으로 넘어간다."""
    monkeypatch.setattr(reddit.time, "sleep", lambda _s: None)
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs["headers"]["User-Agent"]))
        if url.startswith("https://www.reddit.com"):
            return _response(429)
        return _response(200, _ATOM.encode())

    with mock.patch.dict(os.environ, {}, clear=False):
        os.environ.pop("REDDIT_CLIENT_ID", None)
        os.environ.pop("REDDIT_CLIENT_SECRET", None)
        with mock.patch.object(requests, "get", fake_get):
            items = reddit.fetch(_CFG)

    # www 조합(즉시 + 백오프 재시도)이 모두 429면 old 호스트로 내려간다
    assert calls[0][0].startswith("https://www.reddit.com")
    assert calls[-1][0].startswith("https://old.reddit.com")
    # per_subreddit=1 상한 동작까지 확인
    assert len(items) == 1
    assert items[0]["title"] == "First post"


def test_success_first_try_no_fallback():
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs["headers"]["User-Agent"])
        return _response(200, _ATOM.encode())

    with mock.patch.dict(os.environ, {}, clear=False):
        os.environ.pop("REDDIT_CLIENT_ID", None)
        os.environ.pop("REDDIT_CLIENT_SECRET", None)
        with mock.patch.object(requests, "get", fake_get):
            items = reddit.fetch(_CFG)

    assert calls == [reddit.BOT_UA]
    assert len(items) == 1


def test_oauth_path_skips_rss():
    """secret이 있으면 토큰 발급 후 oauth 호스트만 친다 — RSS 요청 0건."""
    listing = {"data": {"children": [
        {"data": {"name": "t3_aaa", "title": "OAuth post",
                  "permalink": "/r/netsec/comments/aaa/",
                  "subreddit": "netsec", "score": 512,
                  "created_utc": 1787000000.0}},
    ]}}

    def fake_post(url, **kwargs):
        assert url == reddit.TOKEN_URL
        resp = _response(200)
        resp.json = lambda: {"access_token": "tok"}
        return resp

    got = []

    def fake_get(url, **kwargs):
        got.append(url)
        assert kwargs["headers"]["Authorization"] == "bearer tok"
        resp = _response(200)
        resp.json = lambda: listing
        return resp

    env = {"REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "sec"}
    with mock.patch.dict(os.environ, env), \
            mock.patch.object(requests, "post", fake_post), \
            mock.patch.object(requests, "get", fake_get):
        items = reddit.fetch(_CFG)

    assert all(u.startswith("https://oauth.reddit.com") for u in got)
    assert len(items) == 1
    assert items[0]["url"] == "https://www.reddit.com/r/netsec/comments/aaa/"
    # 인증 경로는 실제 업보트 수를 쓴다(RSS 폴백은 순위 역산)
    assert items[0]["score"] == 512
    assert items[0]["trend_note"] == "r/netsec ▲512"


def test_oauth_failure_falls_back_to_rss():
    """토큰은 받았지만 listing이 401이면 RSS 폴백으로 살아난다."""
    def fake_post(url, **kwargs):
        resp = _response(200)
        resp.json = lambda: {"access_token": "tok"}
        return resp

    def fake_get(url, **kwargs):
        if url.startswith("https://oauth.reddit.com"):
            return _response(401)
        return _response(200, _ATOM.encode())

    env = {"REDDIT_CLIENT_ID": "id", "REDDIT_CLIENT_SECRET": "sec"}
    with mock.patch.dict(os.environ, env), \
            mock.patch.object(requests, "post", fake_post), \
            mock.patch.object(requests, "get", fake_get):
        items = reddit.fetch(_CFG)

    assert len(items) == 1
    assert items[0]["title"] == "First post"


def test_hard_429_raises():
    # 폴백 체인 전 조합이 429면 raise — 소스별 fail-open은 상위(main)가 처리
    def fake_get(url, **kwargs):
        return _response(429)

    with mock.patch.object(requests, "get", fake_get):
        try:
            reddit.fetch(_CFG)
        except requests.HTTPError:
            pass
        else:
            raise AssertionError("expected HTTPError")


def test_200_with_empty_feed_is_not_success(monkeypatch):
    """old.reddit.com은 차단 시 200 + HTML을 준다 — entry 0건이면 실패 취급.

    이 가드가 없으면 '200인데 수집 0건'으로 조용히 굶는다(2026-08-18 실측).
    """
    monkeypatch.setattr(reddit.time, "sleep", lambda _s: None)
    hosts = []

    def fake_get(url, **kwargs):
        hosts.append(url.split("/r/")[0])
        if url.startswith("https://old.reddit.com"):
            return _response(200, b"<!DOCTYPE html><html>blocked</html>")
        return _response(200, _ATOM.encode())

    with mock.patch.dict(os.environ, {}, clear=False):
        os.environ.pop("REDDIT_CLIENT_ID", None)
        os.environ.pop("REDDIT_CLIENT_SECRET", None)
        with mock.patch.object(requests, "get", fake_get):
            items = reddit.fetch(_CFG)

    # www가 진짜 Atom을 주므로 old까지 내려가지 않는다
    assert hosts[0] == "https://www.reddit.com"
    assert len(items) == 1


def test_all_blocked_or_empty_raises(monkeypatch):
    """전 조합이 차단 페이지(200+빈 피드)면 조용한 0건이 아니라 예외."""
    monkeypatch.setattr(reddit.time, "sleep", lambda _s: None)

    def fake_get(url, **kwargs):
        return _response(200, b"<!DOCTYPE html><html>blocked</html>")

    with mock.patch.dict(os.environ, {}, clear=False):
        os.environ.pop("REDDIT_CLIENT_ID", None)
        os.environ.pop("REDDIT_CLIENT_SECRET", None)
        with mock.patch.object(requests, "get", fake_get):
            try:
                reddit.fetch(_CFG)
            except RuntimeError:
                pass
            else:
                raise AssertionError("expected RuntimeError")
