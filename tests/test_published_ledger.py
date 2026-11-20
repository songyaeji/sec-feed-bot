"""발행 원장 — 날짜를 넘는 카드 중복 판정 테스트. LLM은 전부 모킹.

고정하는 사용자 결정(2026-11-20):
  - 같은 사건에 새 사실이 없으면 절대 재발행하지 않는다.
  - 새 사실이 있으면 '후속' 표기로 허용한다.
  - LLM 판정이 없으면 유사 사건은 제외한다(fail-closed).
"""
import json
import os
import sys
from datetime import date
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import librarian  # noqa: E402
import published_ledger as pl  # noqa: E402

LEDGER = [
    {"date": "2026-11-14", "lane": "news", "url": "https://thehackernews.com/fbi-dprk",
     "title": "FBI says North Korean hackers stole $400 million",
     "title_ko": "FBI 북한 해커 4억 달러 암호화폐 도난", "summary_ko": "", "cves": []},
    {"date": "2026-11-16", "lane": "news", "url": "https://bleepingcomputer.com/sckit",
     "title": "New worm-like SCKit malware targets MSPs",
     "title_ko": "SCKit 웜형 악성코드 MSP 표적", "summary_ko": "", "cves": []},
    {"date": "2026-11-16", "lane": "cve", "url": "https://nvd.nist.gov/CVE-2026-1111",
     "title": "CVE-2026-1111", "title_ko": "", "summary_ko": "", "cves": ["CVE-2026-1111"]},
]


def _cand(i, title, title_ko, url=None, summary=""):
    return {"id": i, "title": title, "title_ko": title_ko, "summary": summary,
            "summary_ko": "요약이다.", "url": url or f"https://example.com/{i}"}


def _fake_llm(monkeypatch, results):
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "x")
    payload = json.dumps({"result": json.dumps({"results": results})})
    monkeypatch.setattr(librarian, "_run_claude_json",
                        lambda *a, **k: SimpleNamespace(returncode=0, stdout=payload))


def test_url_key_folds_scheme_www_slash():
    assert pl.url_key("https://www.Example.com/a/") == pl.url_key("http://example.com/a")


def test_same_url_dropped_without_llm():
    c = [_cand("1", "anything", "아무거나 다른 제목", url="https://www.thehackernews.com/fbi-dprk/")]
    assert pl.filter_news(c, LEDGER, allow_llm=False) == []


def test_llm_same_is_dropped_followup_is_labelled(monkeypatch):
    _fake_llm(monkeypatch, {
        "1": {"verdict": "same", "of": 1, "new_fact": None},
        "2": {"verdict": "followup", "of": 2, "new_fact": "피해 MSP 120곳으로 확대됐다."},
        "3": {"verdict": "new", "of": None, "new_fact": None},
    })
    cands = [
        _cand("1", "North Korean hackers stole $400M via fake video calls",
              "북한 해커 가짜 화상회의로 4억 달러 탈취"),
        _cand("2", "SCKit victims grow", "SCKit 피해 MSP 120곳으로 확대"),
        _cand("3", "Unrelated breach", "국내 보험사 개인정보 유출"),
    ]
    kept = pl.filter_news(cands, LEDGER)
    assert [k["id"] for k in kept] == ["2", "3"]
    assert kept[0]["followup"] is True
    assert kept[0]["followup_of"]["date"] == "2026-11-16"
    assert "120곳" in kept[0]["followup_fact"]
    assert not kept[1].get("followup")


def test_llm_failure_falls_back_to_similarity_fail_closed(monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    cands = [
        _cand("1", "New worm-like SCKit malware targets MSPs worldwide",
              "SCKit 웜형 악성코드 MSP 표적 확산"),
        _cand("2", "Totally different story", "국내 대학 개인정보 유출"),
    ]
    kept = pl.filter_news(cands, LEDGER)
    assert [k["id"] for k in kept] == ["2"]


def test_same_without_reference_is_not_trusted(monkeypatch):
    """근거(of) 없는 same은 결정적 판정으로 — 비슷하지 않으면 남긴다."""
    _fake_llm(monkeypatch, {"1": {"verdict": "same", "of": None}})
    kept = pl.filter_news([_cand("1", "Fresh topic", "새 사건 하나")], LEDGER)
    assert [k["id"] for k in kept] == ["1"]


def test_excessive_same_verdicts_are_discarded(monkeypatch):
    """신뢰 불가 입력이 '전부 같은 사건'으로 카드를 비우는 경로 차단."""
    _fake_llm(monkeypatch, {str(i): {"verdict": "same", "of": 1} for i in range(1, 5)})
    cands = [_cand(str(i), f"distinct story {i} alpha{i}", f"서로 다른 사건 {i}번 제목")
             for i in range(1, 5)]
    assert len(pl.filter_news(cands, LEDGER)) == 4


def test_cve_lane_drops_sent_url_and_cve():
    items = [
        {"id": "a", "title": "CVE-2026-1111 (CVSS 9.8)", "summary": "", "url": "https://x/a"},
        {"id": "b", "title": "Elecbrakes advisory", "summary": "",
         "url": "https://bleepingcomputer.com/sckit"},
        {"id": "c", "title": "CVE-2026-2222 (CVSS 9.1)", "summary": "", "url": "https://x/c"},
    ]
    assert [i["id"] for i in pl.filter_cve_lane(items, LEDGER)] == ["c"]


def test_record_and_prune():
    news = [{"title": "t", "title_ko": "제목", "summary_ko": "**굵은** 요약이다.",
             "summary": "CVE-2026-3333", "url": "https://n", "followup": True}]
    out = pl.record([{"date": "2026-09-01", "url": "old"}], news, [], "2026-11-20")
    assert len(out) == 1  # 30일 넘은 항목 prune
    assert out[0]["summary_ko"] == "굵은 요약이다."
    assert out[0]["cves"] == ["CVE-2026-3333"] and out[0]["followup"] is True
    assert pl.prune([{"date": "2026-10-21"}, {"date": "2026-10-20"}], date(2026, 11, 20)) == [
        {"date": "2026-10-21"}]


def test_merge_union_by_date_url():
    a = [{"date": "2026-11-19", "url": "https://x/1", "title_ko": "로컬"}]
    b = [{"date": "2026-11-19", "url": "http://www.x/1", "title_ko": "원격"},
         {"date": "2026-11-18", "url": "https://x/2"}]
    merged = pl.merge(a, b)
    assert len(merged) == 2
    assert any(e.get("title_ko") == "로컬" for e in merged)
