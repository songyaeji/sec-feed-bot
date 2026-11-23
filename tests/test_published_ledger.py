"""발행 원장 — 날짜를 넘는 카드 중복 판정 테스트. LLM은 전부 모킹.

고정하는 사용자 결정(2026-11-20):
  - 같은 사건에 새 사실이 없으면 절대 재발행하지 않는다.
  - 새 사실이 있으면 '후속' 표기로 허용한다.
  - LLM 판정이 없으면 고유 토큰이 겹치는 후보는 이월한다(소진하지 않음).
  - 긴급 카드도 원장에 기록하고 대조한다.
  - FORCE_DIGEST 같은 날 재발행은 그날 digest 몫을 대조에서 뺀다.
"""
import json
import os
import sys
from datetime import date
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dedup  # noqa: E402
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

# 실제 원장 시드와 원 피드에서 옮긴 사례(state/published.json, 2026-11-20 재생성)
REAL_LEDGER = [
    {"date": "2026-10-26", "lane": "news", "url": "https://www.dailysecu.com/?idxno=209045",
     "title": "국제예술대학교 홈페이지 해킹…회원 개인정보 유출, 웹셸 악성파일 발견",
     "title_ko": "국제예술대학교 홈페이지 해킹 개인정보 유출",
     "summary": "국제예술대학교는 10월 22일 홈페이지에 게시한 사과문을 통해 10월 20일 "
                "카페24로부터 해커의 홈페이지 공격으로 회원 개인정보 일부가 유출된 정황을 "
                "통보받았다고 밝혔다.", "summary_ko": "", "cves": []},
    {"date": "2026-11-07", "lane": "news", "url": "https://news.google.com/a/fintech",
     "title": "보안 취약 핀테크, 해킹에 고객정보 이어 돈까지 털려",
     "title_ko": "금융권 해킹 피해 확대 — 47만건 유출·10억원 탈취",
     "summary": "보안 취약 핀테크, 해킹에 고객정보 이어 돈까지 털려", "summary_ko": "", "cves": []},
    {"date": "2026-11-07", "lane": "news", "url": "https://www.dailysecu.com/?idxno=209335",
     "title": "한패스 해킹으로 고객 개인정보 유출…소득금액증명·외국인등록 사실증명까지 노출",
     "title_ko": "한패스 해킹으로 고객 개인정보 유출",
     "summary": "한패스는 2026년 11월 1일 오전 외부 해킹 공격으로 일부 고객의 개인정보가 "
                "유출된 정황을 확인했다. 유출 추정 시점은 11월 1일 오전 4시 38분경이다.",
     "summary_ko": "", "cves": []},
    {"date": "2026-11-08", "lane": "news", "url": "https://news.google.com/a/linux948",
     "title": "OpenAI 파이프라인, 리눅스 커널에서 권한 상승 취약점 948건 발견",
     "title_ko": "Linux 커널 948개 권한상승 취약점 발견",
     "summary": "OpenAI 파이프라인, 리눅스 커널에서 권한 상승 취약점 948건 발견",
     "summary_ko": "", "cves": []},
    {"date": "2026-11-10", "lane": "news", "url": "https://www.bleepingcomputer.com/n-able-offline",
     "title": "N-able N-central 30개 미패치 제로데이",
     "title_ko": "N-able N-central 30개 미패치 제로데이", "summary": "", "summary_ko": "",
     "cves": []},
    {"date": "2026-11-11", "lane": "news", "url": "https://news.google.com/a/fin40",
     "title": "‘금융권 AI 해킹’ 한달간 40건…개인정보 47만3000건 유출",
     "title_ko": "금융권 AI 해킹 40건 유출",
     "summary": "‘금융권 AI 해킹’ 한달간 40건…개인정보 47만3000건 유출",
     "summary_ko": "", "cves": []},
    {"date": "2026-11-14", "lane": "news",
     "url": "https://thehackernews.com/2026/11/fbi-says-north-korean-hackers-stole.html",
     "title": "FBI Says North Korean Hackers Stole Over $400 Million in Crypto Using "
              "Deepfake Video Calls",
     "title_ko": "FBI 북한 해커, 지난 18개월간 4억 달러 암호화폐 도난 — 딥페이크 영상 통화 악용",
     "summary": "The U.S. Federal Bureau of Investigation (FBI) has established that threat "
                "actors tied to North Korea have stolen more than $400 million worth of "
                "cryptocurrency as part of a social engineering scheme codenamed FaceStealer "
                "in the last 18 months.", "summary_ko": "", "cves": []},
]

REPEATS = {
    "linux_948": ("2026-11-09", {
        "title": "OpenAI Launches GPT-6 Cyber After AI Helps Find 81 Firefox Flaws, "
                 "948 Linux Exploits",
        "title_ko": "Linux 취약점 948개 발견, GPT-6 Cyber 모델 출시",
        "summary": "OpenAI on Thursday unveiled GPT-6 Cyber.",
        "url": "https://thehackernews.com/2026/11/openai-launches-gpt-6-cyber.html"}),
    "fbi_400m": ("2026-11-15", {
        "title": "북한 해커, 가짜 화상회의로 가상자산 4억 달러 이상 탈취…미 FBI, "
                 "‘페이스스틸러’ 인프라 압수",
        "title_ko": "북한 해커, 가짜 화상회의로 가상자산 4억 달러 이상 탈취…미 FBI, "
                    "‘페이스스틸러’ 인프라 압수",
        "summary": "미 법무부가 북한 해커의 가상자산 탈취 캠페인 ‘페이스스틸러(FaceStealer)’에 "
                   "쓰인 클라우드 인프라를 압수했다. 미 연방수사국(FBI)에 따르면 공격자들은 "
                   "최근 18개월 동안 4억 달러 이상의 가상자산을 탈취했다.",
        "url": "https://www.dailysecu.com/?idxno=209508"}),
    "fin_470k": ("2026-11-16", {
        "title": "사일런트푸시, 공격 준비 단계부터 추적…‘미래 공격 지표’로 선제 대응",
        "title_ko": "국내 금융권 37곳 40건 침해, 47만 명 정보 유출",
        "summary": "한 달여 사이 국내 금융회사 37곳에서 침해사고 40건이 신고됐다. 고객과 "
                   "임직원 정보 약 47만3천여 건이 유출됐다. 약 10억 원 규모의 자금 탈취도 "
                   "발생했다.",
        "url": "https://www.dailysecu.com/?idxno=209496"}),
}

DISTINCT = {
    "kb_capital": ("2026-11-14", {
        "title": "KB캐피탈 해킹으로 개인정보 1,811명 유출, 고객 차량번호·임직원 계정정보 노출",
        "title_ko": "KB캐피탈 해킹으로 개인정보 1,811명 유출, 고객 차량번호·임직원 계정정보 노출",
        "summary": "KB캐피탈은 지난 11월 12일 공식 홈페이지에 개인정보 유출 안내문을 "
                   "게시했다. 피해 규모는 고객 20명과 협력업체 직원 및 임직원 1,791명 등 "
                   "총 1,811명이다.",
        "url": "https://www.dailysecu.com/?idxno=209492"}),
    "uos_15": ("2026-11-18", {
        "title": "서울시립대 홈페이지 해킹으로 개인정보 유출...경찰에 수사 의뢰",
        "title_ko": "서울시립대 홈페이지 해킹, 15명 개인정보 유출",
        "summary": "서울시립대학교 홈페이지가 외부 해킹 공격을 받아 구성원 15명의 개인정보가 "
                   "비인가 조회됐다. 해킹은 10월 18일 오후 5시 44분경 발생했으며 11월 3일 "
                   "사고를 인지했다.",
        "url": "https://www.dailysecu.com/?idxno=209554"}),
    # 패치 공개는 미패치 제로데이 카드의 후속(새 사실) — 결정적 판정이 막으면 안 된다
    "n_able_hotfix": ("2026-11-12", {
        "title": "N-able releases security hotfixes for zero-day vulnerabilities",
        "title_ko": "N-able N-central — 공개된 제로데이 긴급패치",
        "summary": "N-able released hotfixes to address zero-day bugs affecting its N-central "
                   "remote monitoring and management (RMM) platform, which were publicly "
                   "disclosed over the weekend.",
        "url": "https://www.bleepingcomputer.com/n-able-hotfix"}),
}

SCKIT_TODAY = [
    {"id": "a", "title": "New worm-like 'SCKit' malware targets MSPs in ScreenConnect attacks",
     "title_ko": "SCKit 웜형 악성코드, ScreenConnect 악용·MSP 표적",
     "summary": "A new worm-like malware toolkit named SCKit was deployed in the recent "
                "ScreenConnect attacks targeting managed service providers (MSPs).",
     "url": "https://www.bleepingcomputer.com/sckit"},
    {"id": "b", "title": "SCKit abuses ScreenConnect to deploy remote access and target "
                         "technician sessions",
     "title_ko": "SCKit abuses ScreenConnect to deploy remote access and target technician sessions",
     "summary": "SCKit abuses ScreenConnect to deploy unauthorized remote access. The post "
                "appeared first on Microsoft Security Blog.",
     "url": "https://www.microsoft.com/security/blog/sckit"},
]


def _cand(i, title, title_ko, url=None, summary="", **extra):
    return {"id": i, "title": title, "title_ko": title_ko, "summary": summary,
            "summary_ko": "요약이다.", "url": url or f"https://example.com/{i}", **extra}


def _fake_llm(monkeypatch, results, seen=None):
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "x")
    payload = json.dumps({"result": json.dumps({"results": results})})

    def run(args, prompt, timeout):
        if seen is not None:
            seen.append(prompt)
        return SimpleNamespace(returncode=0, stdout=payload)

    monkeypatch.setattr(librarian, "_run_claude_json", run)


def test_url_key_folds_scheme_www_slash():
    assert pl.url_key("https://www.Example.com/a/") == pl.url_key("http://example.com/a")


def test_same_url_dropped_without_llm():
    c = [_cand("1", "anything", "아무거나 다른 제목", url="https://www.thehackernews.com/fbi-dprk/")]
    assert pl.filter_news(c, LEDGER, allow_llm=False) == []
    assert not c[0].get("ledger_deferred")  # 같은 URL은 확정 중복이라 소진


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


# --- 결정적 판정: 실제 재게재 4건 차단, 다른 사건 2건과 후속 1건 통과 ----------

@pytest.mark.parametrize("name", sorted(REPEATS))
def test_real_repeats_are_deferred_without_llm(monkeypatch, name):
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    day, item = REPEATS[name]
    cand = dict(item, id=name)
    assert pl.filter_news([cand], REAL_LEDGER, today=day) == []
    assert cand["ledger_deferred"] is True  # 소진하지 않고 이월


@pytest.mark.parametrize("name", sorted(DISTINCT))
def test_distinct_events_are_not_blocked(monkeypatch, name):
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    day, item = DISTINCT[name]
    cand = dict(item, id=name)
    assert pl.filter_news([cand], REAL_LEDGER, today=day) == [cand]
    assert not cand.get("ledger_deferred")


def test_same_day_duplicate_sckit_is_dropped():
    kept, dropped = dedup.dedup_today([dict(c) for c in SCKIT_TODAY])
    assert [k["id"] for k in kept] == ["a"]
    assert [d["id"] for d in dropped] == ["b"]


def test_same_day_advisory_boilerplate_does_not_merge():
    """CISA 권고의 'View CSAF Summary' 상투구와 벤더명만으로 묶지 않는다."""
    a = {"id": "1", "title": "Siemens Industrial Edge App Publisher",
         "summary": "View CSAF Summary The Industrial Edge App Publisher contains a "
                    "vulnerability chain. Siemens has released an update."}
    b = {"id": "2", "title": "Siemens RUGGEDCOM CROSSBOW",
         "summary": "View CSAF Summary RUGGEDCOM CROSSBOW contains multiple vulnerabilities. "
                    "Siemens has released a new version."}
    kept, dropped = dedup.dedup_today([a, b])
    assert len(kept) == 2 and dropped == []


def test_deterministic_window_is_seven_days(monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    cand = dict(REPEATS["fbi_400m"][1], id="x")
    assert pl.filter_news([cand], REAL_LEDGER, today="2026-11-25") == [cand]


def test_quantities_fold_korean_and_english_notation():
    q = dict((v, c) for c, v in dedup._quantities("4억 달러, $400 million, 47만3천여 건"))
    assert q[400_000_000] == "usd" and q[473_000] == "n"
    # 반올림 표기는 같은 수치, 자릿수가 같은 다른 번호는 다른 수치
    assert dedup._same_figure(470_000, 473_000) and dedup._same_figure(1_800, 1_811)
    assert not dedup._same_figure(10_148, 10_144) and not dedup._same_figure(20, 15)
    assert not dedup._same_figure(30_000, 27_001)
    assert not dedup._same_figure(6.3e9, 6.43e9)
    # 날짜, 시각, 연도, CVSS 점수, 버전은 수치가 아니다
    assert dedup._quantities("2026년 11월 1일 오전 4시 38분 CVSS 9.8 v5.4.0 on November 12") == []


def test_llm_unknown_verdict_uses_deterministic_rule(monkeypatch):
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


# --- B3 날짜와 매체, B4 새 사실 없는 후속 ------------------------------------

def test_prompt_carries_candidate_date_and_source(monkeypatch):
    seen: list[str] = []
    _fake_llm(monkeypatch, {"1": {"verdict": "new", "of": None}}, seen)
    cand = _cand("1", "x", "새 사건", published="2026-11-15T01:00:00+00:00",
                 source="데일리시큐")
    pl.filter_news([cand], LEDGER)
    assert "게재 2026-11-15 데일리시큐" in seen[0]
    assert "발행 2026-11-14" in seen[0]


def test_followup_published_before_card_is_same(monkeypatch):
    _fake_llm(monkeypatch, {
        "1": {"verdict": "followup", "of": 1, "new_fact": "FBI가 인프라를 압수했다."},
        "2": {"verdict": "new", "of": None}, "3": {"verdict": "new", "of": None}})
    early = _cand("1", "a", "북한 해커 4억 달러", published="2026-11-13T14:28:58+00:00")
    others = [_cand("2", "b", "다른 사건 둘"), _cand("3", "c", "다른 사건 셋")]
    kept = pl.filter_news([early] + others, LEDGER)
    assert [k["id"] for k in kept] == ["2", "3"]


def test_followup_without_new_fact_is_same(monkeypatch):
    _fake_llm(monkeypatch, {
        "1": {"verdict": "followup", "of": 2, "new_fact": "  "},
        "2": {"verdict": "new", "of": None}, "3": {"verdict": "new", "of": None}})
    cands = [_cand("1", "a", "SCKit 재보도"), _cand("2", "b", "다른 사건 둘"),
             _cand("3", "c", "다른 사건 셋")]
    assert [k["id"] for k in pl.filter_news(cands, LEDGER)] == ["2", "3"]


# --- B5 후보 2건 이하 전부 same ---------------------------------------------

def test_small_set_all_same_without_evidence_is_deferred(monkeypatch):
    _fake_llm(monkeypatch, {"1": {"verdict": "same", "of": 1}})
    cand = _cand("1", "Fresh topic", "새 사건 하나")
    assert pl.filter_news([cand], LEDGER) == []
    assert cand["ledger_deferred"] is True


def test_small_set_all_same_with_evidence_is_dropped(monkeypatch):
    _fake_llm(monkeypatch, {"1": {"verdict": "same", "of": 7}})
    cand = dict(REPEATS["fbi_400m"][1], id="1")
    assert pl.filter_news([cand], REAL_LEDGER, today="2026-11-15") == []
    assert not cand.get("ledger_deferred")


# --- B6 빈 URL, B7 후속 필드 초기화 -------------------------------------------

def test_empty_url_is_never_a_key():
    ledger = [{"date": "2026-11-16", "lane": "news", "url": "", "title": "a",
               "title_ko": "가", "cves": []},
              {"date": "2026-11-16", "lane": "cve", "url": "", "title": "b", "cves": []}]
    cand = _cand("1", "other", "다른 사건", url="")
    assert pl.filter_news([cand], ledger, allow_llm=False, today="2026-11-17") == [cand]
    assert pl.filter_cve_lane([{"id": "c", "title": "x", "url": ""}], ledger) != []
    merged = pl.merge([ledger[0]], [dict(ledger[0], title="c", title_ko="다")])
    assert len(merged) == 2


def test_stale_followup_fields_are_cleared(monkeypatch):
    _fake_llm(monkeypatch, {"1": {"verdict": "new", "of": None}})
    stale = _cand("1", "x", "새 사건", followup=True, followup_of={"date": "d"},
                  followup_fact="옛 사실", ledger_deferred=True)
    kept = pl.filter_news([stale], LEDGER)
    assert kept == [stale]
    assert not set(pl.FOLLOWUP_FIELDS) & set(stale)
    again = _cand("2", "x", "원장 없음", followup=True)
    pl.filter_news([again], [])
    assert "followup" not in again


# --- 긴급 카드 원장, FORCE_DIGEST ------------------------------------------

def test_urgent_cards_are_recorded_and_compared(monkeypatch):
    urgent = [{"title": "Breaking breach", "summary": "CVE-2026-7777 exploited",
               "url": "https://x/urgent"}]
    out = pl.record_urgent([], urgent, "2026-11-20")
    assert out[0]["lane"] == "urgent" and out[0]["cves"] == ["CVE-2026-7777"]
    assert out[0]["summary"] == "CVE-2026-7777 exploited"
    cand = _cand("1", "Breaking breach", "속보", url="https://x/urgent")
    assert pl.filter_news([cand], out, allow_llm=False, today="2026-11-20") == []
    assert pl.filter_cve_lane([{"title": "CVE-2026-7777", "url": "https://n/7777"}], out) == []
    seen: list[str] = []
    _fake_llm(monkeypatch, {"1": {"verdict": "new", "of": None}}, seen)
    pl.filter_news([_cand("2", "y", "다른 사건")], out)
    assert "[발행 2026-11-20 긴급] Breaking breach" in seen[0]


def test_force_digest_excludes_todays_digest_entries():
    ledger = [
        {"date": "2026-11-16", "lane": "news", "url": "https://x/news", "title": "n"},
        {"date": "2026-11-16", "lane": "urgent", "url": "https://x/urgent", "title": "u"},
        {"date": "2026-11-16", "lane": "cve", "url": "https://x/cve", "title": "c",
         "cves": ["CVE-2026-1111"]},
    ]
    a = _cand("1", "n", "오늘 낸 뉴스", url="https://x/news")
    b = _cand("2", "u", "오늘 낸 긴급", url="https://x/urgent")
    kept = pl.filter_news([a, b], ledger, allow_llm=False, exclude_date="2026-11-16",
                          today="2026-11-16")
    assert kept == [a]  # 긴급 카드는 재발행 대상이 아니라 계속 대조
    item = {"title": "CVE-2026-1111", "url": "https://x/cve"}
    assert pl.filter_cve_lane([item], ledger) == []
    assert pl.filter_cve_lane([item], ledger, exclude_date="2026-11-16") == [item]


# --- 기록 ---------------------------------------------------------------

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
    assert out[0]["summary"] == "CVE-2026-3333"
    assert out[0]["cves"] == ["CVE-2026-3333"] and out[0]["followup"] is True
    assert pl.record(out, news, [], "2026-11-20") == out  # 같은 날 재기록은 한 줄
    assert pl.prune([{"date": "2026-10-21"}, {"date": "2026-10-20"}], date(2026, 11, 20)) == [
        {"date": "2026-10-21"}]


def test_merge_union_by_date_url():
    a = [{"date": "2026-11-19", "url": "https://x/1", "title_ko": "로컬"}]
    b = [{"date": "2026-11-19", "url": "http://www.x/1", "title_ko": "원격"},
         {"date": "2026-11-18", "url": "https://x/2"}]
    merged = pl.merge(a, b)
    assert len(merged) == 2
    assert any(e.get("title_ko") == "로컬" for e in merged)


def test_llm_followup_without_shared_subject_is_not_labelled(monkeypatch):
    # 2026-11-20 QA 실행: 다른 사건(정부 냉동 유통망 권고 vs 유럽 슈퍼마켓 냉동
    # 시스템 이란 귀속)을 후속으로 판정했다. 겹치는 CVE나 이름이 없으면 새 기사
    _fake_llm(monkeypatch, {
        "1": {"verdict": "followup", "of": 2, "new_fact": "점검 권고가 나왔다."},
    })
    cand = _cand("1", "Government urges cold chain security checks",
                 "정부, 냉장 냉동 유통망 보안 위험 점검 권고")
    kept = pl.filter_news([cand], LEDGER)
    assert [k["id"] for k in kept] == ["1"]
    assert not kept[0].get("followup")


def test_llm_followup_with_shared_figure_is_labelled(monkeypatch):
    # 2026-11-23 QA 실행: '금융기관 16곳 해킹 조사 완료'가 '금융권 16곳 해킹'과
    # 이름은 안 겹치고 수치만 겹쳐 후속 표기를 잃었다
    ledger = [{"date": "2026-11-06", "lane": "news", "url": "https://e.com/16",
               "title": "금융권 16곳 해킹", "title_ko": "금융권 16곳 해킹, 망분리 규제 재설계",
               "summary": "", "cves": []}]
    _fake_llm(monkeypatch, {
        "1": {"verdict": "followup", "of": 1, "new_fact": "경찰이 조사를 마쳤다."},
    })
    cand = _cand("1", "Police finish probe into 16 financial firms hack",
                 "경찰, 금융기관 16곳 해킹 조사 완료")
    kept = pl.filter_news([cand], ledger, today="2026-11-20")
    assert kept and kept[0].get("followup") is True
