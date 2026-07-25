"""sources/reddit.py 단위 테스트 — 전 요청 모킹(오프라인 안전).

핵심 검증: 봇 UA가 429를 맞으면 브라우저 UA로 1회 재시도한다
(2026-07-25 Actions 데이터센터 IP 상시 429 사고의 재발 방지 가드).
"""
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


def test_429_falls_back_to_browser_ua():
    calls = []

    def fake_get(url, **kwargs):
        ua = kwargs["headers"]["User-Agent"]
        calls.append(ua)
        if ua.startswith("sec-feed-bot"):
            return _response(429)
        return _response(200, _ATOM.encode())

    with mock.patch.object(requests, "get", fake_get):
        items = reddit.fetch(_CFG)

    assert len(calls) == 2
    assert calls[0].startswith("sec-feed-bot")
    assert calls[1].startswith("Mozilla")
    # per_subreddit=1 상한 동작까지 확인
    assert len(items) == 1
    assert items[0]["title"] == "First post"


def test_success_first_try_no_fallback():
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs["headers"]["User-Agent"])
        return _response(200, _ATOM.encode())

    with mock.patch.object(requests, "get", fake_get):
        items = reddit.fetch(_CFG)

    assert calls == ["sec-feed-bot/1.0"]
    assert len(items) == 1


def test_hard_429_raises():
    # 브라우저 UA 재시도까지 429면 raise — 소스별 fail-open은 상위(main)가 처리
    def fake_get(url, **kwargs):
        return _response(429)

    with mock.patch.object(requests, "get", fake_get):
        try:
            reddit.fetch(_CFG)
        except requests.HTTPError:
            pass
        else:
            raise AssertionError("expected HTTPError")
