"""카드 문안 재작성·검증 테스트. LLM·네트워크는 전부 모킹.

사용자 보고(2026-11-20)를 회귀로 고정한다:
  1. 용어 칸에 기업·기관 이름 금지
  3. 기사와 안 맞는 태그 금지(취약점 권고에 '침해', 근거 없는 RCE)
  4. 원문 그대로(구글뉴스 매체 제목 나열) 금지
  6. 영어 미번역 카드 금지 — 검증 실패 항목은 빠진다
"""
import json
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import card_editor as ce  # noqa: E402
import librarian  # noqa: E402

GOOD = {
    "title_ko": "노란우산 개인정보 36만건 유출",
    "summary_ko": "**노란우산** 홈페이지가 해킹돼 가입자 36만명의 정보가 유출됐다. 중소벤처기업부는 경찰에 수사를 의뢰했다.",
    "why_ko": "공제 가입자 대상 2차 피싱 위험이 크다.",
    "term_ko": "크리덴셜 스터핑 — 유출된 계정정보를 다른 사이트에 대입하는 공격",
    "term_type": "보안용어",
    "tags_ko": ["개인정보유출사고", "공제회", "국내사고"],
}


def test_title_requires_korean():
    assert ce.validate_title("Policy and Disclosure: 2026 Edition") is None
    assert ce.validate_title("Siemens SIMATIC 인증 우회") == "Siemens SIMATIC 인증 우회"


def test_summary_rejects_english_and_noun_endings():
    assert ce.validate_summary("Since 2021, Project Zero has followed a 90+30 policy.") is None
    assert ce.validate_summary("금융보안원 해킹 정리.") is None  # '~다'로 안 끝남
    assert ce.validate_summary(GOOD["summary_ko"])


def test_term_rejects_company_and_agency_names():
    assert ce.validate_term("금융보안원 — 금융권 보안 전담 기관") is None
    assert ce.validate_term("Elecbrakes Inc — 트레일러 제동 장치 제조사") is None
    assert ce.validate_term("RCE — 원격에서 임의 코드를 실행하는 공격", "고유명사") is None
    assert ce.validate_term("RCE — 원격에서 임의 코드를 실행하는 공격", "보안용어")
    assert ce.validate_term("사이버보험 — 해킹 피해를 보상하는 보험")  # '보험'으로 끝나도 용어


def test_tags_must_match_article():
    text = "Elecbrakes trailer brake firmware tampering, missing authentication"
    tags = ce.validate_tags(["ICS침해", "RCE", "제동시스템", "차량보안"], "vuln", text)
    assert "ICS침해" not in tags          # 사고 아닌 항목에 '침해'
    assert "RCE" not in tags              # 본문 근거 없는 약어
    assert tags == ["제동시스템", "차량보안"]
    assert ce.validate_tags(["RCE", "원격코드실행"], "vuln", "remote code execution flaw") == [
        "RCE", "원격코드실행"]
    assert ce.validate_tags(["금융", "보안"], "incident", "") == []  # 넓은 한 단어


def test_rce_inside_word_is_not_evidence():
    assert ce.validate_tags(["RCE", "공급망공격"], "incident", "open source resource") == ["공급망공격"]


def test_extract_paragraphs_prefers_article():
    html = ("<html><nav><p>메뉴 메뉴 메뉴 메뉴 메뉴 메뉴 메뉴 메뉴 메뉴 메뉴</p></nav>"
            "<article>" + "<p>본문 문단입니다. 충분히 긴 문장으로 구성돼 있다.</p>" * 20
            + "</article><p>광고 문구가 여기 들어갑니다 아주 길게 길게 길게</p></html>")
    text = ce.extract_paragraphs(html)
    assert text.startswith("본문 문단입니다")
    assert "메뉴" not in text and "광고" not in text


def test_google_news_links_are_not_fetched():
    assert ce.fetch_article("https://news.google.com/rss/articles/CBMi") == ""


def _fake_llm(monkeypatch, items):
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "x")
    payload = json.dumps({"result": json.dumps({"items": items})})
    monkeypatch.setattr(librarian, "_run_claude_json",
                        lambda *a, **k: SimpleNamespace(returncode=0, stdout=payload))


def test_rewrite_uses_llm_fields_and_drops_unfixable(monkeypatch):
    _fake_llm(monkeypatch, {
        "1": GOOD,
        "2": {"title_ko": "Policy and Disclosure", "summary_ko": "English only."},
        "3": {"desc_ko": "Siemens SIMATIC 인증 우회 취약점"},
    })
    news = [
        {"id": "a", "title": "Yellow umbrella breach", "kind": "incident", "url": "u1"},
        # 사서 문안도 영어 — 재작성 실패 시 대체 문안도 검증에 걸려 빠져야 한다
        {"id": "b", "title": "Policy and Disclosure: 2026 Edition", "url": "u2",
         "title_ko": "Policy and Disclosure: 2026 Edition"},
    ]
    cve = [{"id": "c", "title": "ICSA-26-321-08 Siemens SIMATIC", "lane": "cve"}]
    kept_news, kept_cve = ce.rewrite(news, cve, fetch=False)
    assert [n["id"] for n in kept_news] == ["a"]
    assert kept_news[0]["term_ko"].startswith("크리덴셜 스터핑")
    assert kept_news[0]["tags_ko"] == ["개인정보유출사고", "공제회", "국내사고"]
    assert kept_cve[0]["title_ko"] == "Siemens SIMATIC 인증 우회 취약점"


def test_rewrite_failure_falls_back_to_valid_draft(monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    news = [dict(GOOD, id="a", title="x", url="u", kind="incident",
                 term_ko="금융보안원 — 금융권 보안 기관")]
    kept, _ = ce.rewrite(news, [], fetch=False)
    assert kept[0]["title_ko"] == GOOD["title_ko"]
    assert kept[0]["term_ko"] is None  # 사서 초안의 기관명 용어는 버려진다


def test_google_news_headline_list_is_not_a_valid_summary():
    raw = ("금융위, '해킹 사고' 금융보안원 현장 점검 MBC 뉴스 '해킹사고' 금융보안원 찾은 "
           "신진창 부위원장 머니투데이 금융위, 금융보안원 침해사고에 유감 표명 Chosunbiz")
    assert ce.validate_summary(raw) is None
