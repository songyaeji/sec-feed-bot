"""sources/mastodon.py 단위 테스트 — 전 요청 모킹(오프라인 안전).

Reddit 트렌드를 대체한 소스(2026-08-18). 고정하는 계약 세 가지:
① 화제성 점수 = 최근 2일 공유 횟수 합, min_shares 미만은 드롭.
② 키워드는 단어 경계로 맞춘다 — 부분 문자열 매칭이 "ai"를 Airtag·
   against 안에서 잡아 야생동물·정치 기사를 통과시켰던 실측 오탐 방지.
③ 제목 없거나 http(s)가 아닌 링크는 경계에서 드롭.
"""
import os
import sys
from unittest import mock

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources import mastodon  # noqa: E402

_CFG = {"name": "Mastodon 화제 링크", "host": "infosec.exchange",
        "limit": 20, "min_shares": 30}


def _link(title, url, uses=(100, 50), description="", provider="Example",
          published="2026-08-17T13:16:09.000Z"):
    return {
        "url": url,
        "title": title,
        "description": description,
        "provider_name": provider,
        "published_at": published,
        "history": [{"day": "1787011200", "accounts": "1", "uses": str(u)}
                    for u in uses],
    }


def _patch_get(payload):
    resp = requests.Response()
    resp.status_code = 200
    resp.json = lambda: payload
    return mock.patch.object(requests, "get", lambda url, **kw: resp)


def test_score_sums_recent_two_days_and_drops_cold_links():
    payload = [
        _link("AI model release", "https://example.com/a", uses=(80, 40, 999)),
        _link("AI side note", "https://example.com/b", uses=(10, 5)),
    ]
    with _patch_get(payload):
        items = mastodon.fetch(dict(_CFG, keywords=["ai"]))

    # 120 = 80+40 (셋째 날 999는 창 밖), 15는 min_shares 30 미만이라 드롭
    assert [it["score"] for it in items] == [120]
    assert items[0]["trend_note"] == "Example · 120회 공유"


def test_keyword_matches_on_word_boundary_only():
    """'ai'가 Airtag/against 안에서 걸리면 안 된다(2026-08-18 실측 오탐)."""
    payload = [
        _link("Hidden Airtag reveals warehouse against rules",
              "https://example.com/noise"),
        _link("New AI agent ships today", "https://example.com/hit"),
    ]
    with _patch_get(payload):
        items = mastodon.fetch(dict(_CFG, keywords=["ai"]))

    assert [it["url"] for it in items] == ["https://example.com/hit"]


def test_star_suffix_enables_prefix_match():
    payload = [
        _link("Two vulnerabilities patched", "https://example.com/v"),
        _link("Unrelated cooking post", "https://example.com/x"),
    ]
    with _patch_get(payload):
        items = mastodon.fetch(dict(_CFG, keywords=["vulnerabilit*"]))

    assert [it["url"] for it in items] == ["https://example.com/v"]


def test_keyword_hits_summary_and_url_too():
    payload = [
        _link("Opaque headline", "https://example.com/mcp-server",
              description="A plain description"),
        _link("Another opaque one", "https://example.com/zzz",
              description="Explains prompt injection defenses"),
        _link("Third opaque one", "https://example.com/yyy",
              description="Nothing relevant here"),
    ]
    with _patch_get(payload):
        items = mastodon.fetch(dict(_CFG, keywords=["mcp", "prompt*"]))

    assert len(items) == 2


def test_empty_keywords_disables_filter():
    payload = [_link("Anything at all", "https://example.com/a")]
    with _patch_get(payload):
        assert len(mastodon.fetch(dict(_CFG, keywords=[]))) == 1


def test_drops_untitled_and_non_http_links():
    payload = [
        _link("", "https://example.com/untitled"),
        _link("AI thing", "javascript:alert(1)"),
        _link("AI good", "https://example.com/ok"),
    ]
    with _patch_get(payload):
        items = mastodon.fetch(dict(_CFG, keywords=["ai"]))

    assert [it["url"] for it in items] == ["https://example.com/ok"]


def test_id_namespaced_by_host():
    payload = [_link("AI thing", "https://example.com/a")]
    with _patch_get(payload):
        items = mastodon.fetch(dict(_CFG, keywords=["ai"]))

    assert items[0]["id"] == "masto-infosec.exchange-https://example.com/a"
