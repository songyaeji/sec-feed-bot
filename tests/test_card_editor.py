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
    "summary_ko": "**노란우산** 홈페이지가 크리덴셜 스터핑 공격을 받아 가입자 36만명의 정보가 유출됐다. 중소벤처기업부는 경찰에 수사를 의뢰했다.",
    "why_ko": "공제 가입자 대상 2차 피싱 위험이 크다.",
    "term_ko": "크리덴셜 스터핑 — 유출된 계정정보를 다른 사이트에 대입하는 공격",
    "term_type": "보안용어",
    "tags_ko": ["개인정보유출사고", "공제회", "국내사고"],
    "region": "국내",
}
# GOOD 태그의 근거가 되는 원문(국문 피드 요약)
GOOD_SOURCE = "노란우산공제회 홈페이지가 해킹돼 가입자 개인정보 36만건이 유출됐다. 국내 소상공인 피해가 우려된다."


def test_title_requires_korean():
    assert ce.validate_title("Policy and Disclosure: 2026 Edition") is None
    assert ce.validate_title("Siemens SIMATIC 인증 우회") == "Siemens SIMATIC 인증 우회"


def test_title_rejects_english_headline_with_korean_tail():
    # QA C4: 한글 4자만 붙이면 통과하던 영어 원제
    for t in ("Fortinet warns of new FortiWeb zero-day exploited in attacks 긴급 경고",
              "해킹 사고 Retadup Worm Resurfaces 7 Years After Takedown to Spread CoffeeLoader Malware",
              "쿠팡 says data of 33.7 million customers exposed in breach",
              "VeloCloud SQL injection 제로데이 권한상향 가능"):
        assert ce.validate_title(t) is None, t
    for t in ("Ivanti Connect Secure 제로데이 악용", "러시아 APT28, NATO 해군 조선소 침해",
              "Microsoft Exchange Server 긴급 패치 배포"):
        assert ce.validate_title(t) == t


def test_summary_rejects_english_and_noun_endings():
    assert ce.validate_summary("Since 2021, Project Zero has followed a 90+30 policy.") is None
    assert ce.validate_summary("금융보안원 해킹 정리.") is None  # '~다'로 안 끝남
    assert ce.validate_summary(GOOD["summary_ko"])


def test_summary_english_phrase_rule_replaces_hangul_ratio():
    # QA C5: 영어 구 삽입은 비율 0.5를 통과했다
    assert ce.validate_summary(
        "보안업체에 따르면 attackers used stolen credentials to access the network 상황이다. "
        "피해 기업은 조사를 시작했다.") is None
    # 고유명사가 많아 비율이 낮아도 정상 요약은 통과(비율 0.5 시절 탈락)
    ok = ("**Microsoft SharePoint Server** CVE-2026-1234가 KEV에 추가됐다. "
          "CISA는 FCEB 기관에 3주 안에 패치를 적용하라고 지시했다.")
    assert ce.validate_summary(ok) == ok
    # 한글 20자 미만
    assert ce.validate_summary("Mandiant가 LLMjacking을 분석했다.") is None


def test_summary_rejects_raw_copy_of_source():
    # QA C6: 원문 리드를 그대로 옮긴 요약(60자 이상 공통 구간)
    lead = ("금융보안원 상시평가 시스템이 해킹돼 공격자가 금융감독원 수준의 접근 권한을 확보한 것으로 "
            "드러났다. 금융위원회는 현장 점검에 나섰다.")
    assert ce.validate_summary(lead, (lead,)) is None
    assert ce.validate_summary(lead, ("", "다른 기사 본문이다.")) == lead
    short = "금융보안원 상시평가 시스템이 해킹돼 공격자가 높은 권한을 얻었다. 금융위는 점검에 착수했다."
    assert ce.validate_summary(short, (lead,)) == short  # 공통 구간 60자 미만


def test_term_rejects_company_and_agency_names():
    assert ce.validate_term("금융보안원 — 금융권 보안 전담 기관") is None
    assert ce.validate_term("Elecbrakes Inc — 트레일러 제동 장치 제조사") is None
    assert ce.validate_term("RCE — 원격에서 임의 코드를 실행하는 공격", "고유명사") is None
    assert ce.validate_term("RCE — 원격에서 임의 코드를 실행하는 공격", "보안용어")
    assert ce.validate_term("사이버보험 — 해킹 피해를 보상하는 보험")  # '보험'으로 끝나도 용어


# QA C1 실측 세트 일부. 사서 폴백 경로는 term_type이 없다(None)
ENTITY_TERMS = [
    "CISA — 미국 사이버보안 인프라 보안청",
    "국정원 — 국가 사이버안보를 총괄하는 정보기관",
    "과기정통부 — 정보보호 정책을 맡는 정부 부처",
    "경찰청 — 사이버 범죄를 수사하는 경찰 조직",
    "Microsoft — 윈도와 애저를 만드는 미국 기업",
    "삼성전자 — 국내 최대 전자 기업",
    "SK텔레콤 — 국내 1위 이동통신사",
    "쿠팡 — 국내 최대 이커머스 플랫폼",
    "롯데카드 — 국내 신용카드사",
    "노란우산공제 — 소상공인 퇴직금 성격의 공제 제도",
    "LockBit — 서비스형 랜섬웨어",
    "Volt Typhoon — 중국 배후 국가 지원 해킹 그룹",
    "라자루스 — 북한 정찰총국 산하 해킹 조직",
    "APT28 — 러시아 군 정보기관 연계 해킹 조직",
    "PAN-OS — 팔로알토 방화벽 운영체제",
    "Exchange Server — 마이크로소프트의 메일 서버",
    "방위사업청 — 방산 보안을 관리하는 정부 기관",
    "신한카드 — 국내 신용카드사",
    "토스 — 간편송금 핀테크 서비스",
    "Copilot — 마이크로소프트의 AI 비서",
    "한패스 — 해외송금 및 외국인 대상 금융 생활 서비스 제공하는 핀테크",
    "Operation FlashHole — Lazarus의 금융 표적 공격 작전",
]
SECURITY_TERMS = [
    "크리덴셜 스터핑 — 유출된 계정정보를 다른 사이트에 대입하는 공격",
    "MFA 피로 공격 — 인증 요청을 반복해 승인을 유도하는 공격",
    "ISMS-P — 정보보호와 개인정보보호 관리체계 인증",
    "EDR — 단말의 위협을 탐지하고 대응하는 솔루션",
    "SQL 인젝션 — 입력값에 SQL 구문을 넣어 DB를 조작하는 공격",
    "서비스형 랜섬웨어 — 랜섬웨어를 임대해 주는 범죄 사업 모델",
    "초기 접근 브로커 — 침투한 기업 접근권을 판매하는 범죄자",
    "C2 서버 — 감염 기기에 명령을 내리는 공격자 서버",
    "IMSI — 국제 모바일 구독자 ID, 무선 신호로 노출되는 식별자",
    "OAuth 토큰 탈취 — 인증 토큰을 훔쳐 계정에 접근하는 수법",
    "프록시 — 트래픽을 중개하는 서버, 추적 회피와 익명성 유지에 사용",
    "정보보호 공시 — 기업의 보안 투자 현황을 공개하는 제도",
]


def test_term_rejects_entities_without_term_type():
    for term in ENTITY_TERMS:
        assert ce.validate_term(term) is None, term
        assert ce.validate_term(term, "보안용어") is None, term  # 자기신고로 못 넘는다


def test_term_keeps_real_security_terms():
    for term in SECURITY_TERMS:
        assert ce.validate_term(term) == term, term
        assert ce.validate_term(term, "보안 용어") == term, term  # 공백 표기 차이 허용


def test_tags_must_match_article():
    text = ("Elecbrakes trailer brake controller lets attackers bypass authentication "
            "and tamper with firmware")
    tags = ce.validate_tags(["ICS침해", "RCE", "인증우회", "펌웨어변조", "네트워크기기"], "vuln", text)
    assert "ICS침해" not in tags          # 사고 아닌 항목에 '침해'
    assert "RCE" not in tags              # 본문 근거 없는 약어
    assert "펌웨어변조" not in tags        # 표에 없는 한글 조각은 원문에 글자 그대로 있어야
    assert tags == ["인증우회"]           # 네트워크기기는 network, device 근거 없음
    assert ce.validate_tags(["RCE", "원격코드실행"], "vuln", "remote code execution flaw") == [
        "RCE", "원격코드실행"]
    assert ce.validate_tags(["금융", "보안"], "incident", "") == []  # 넓은 한 단어


def test_rce_inside_word_is_not_evidence():
    assert ce.validate_tags(["RCE", "공급망공격"], "incident",
                            "open source resource supply chain attack") == ["공급망공격"]


def test_korean_and_mixed_tags_need_source_evidence():
    # QA C3: 한글 태그와 혼합 태그는 근거 검사가 없었다
    en = "North Korean hackers deployed an infostealer through a fake npm package"
    assert ce.validate_tags(["북한해킹", "인포스틸러", "공급망공격"], "incident", en) == [
        "북한해킹", "인포스틸러"]
    assert ce.validate_tags(["랜섬웨어", "딥페이크"], "incident", en) == []
    assert ce.validate_tags(["RCE취약점", "C2서버", "CVE-2026-9999"], "vuln",
                            "CVE-2026-9999 lets attackers reach a C2 server") == [
        "C2서버", "CVE-2026-9999"]
    ko = "노란우산공제회 홈페이지가 해킹돼 개인정보가 유출됐다."
    # 노란우산은 근거는 있지만 기관명이라 태그에서 빠진다(2026-11-23 QA)
    assert ce.validate_tags(["개인정보유출", "노란우산", "제로데이"], "incident", ko) == [
        "개인정보유출"]
    # 본문 공백을 메워 다른 낱말에서 근거를 찾지 않는다('제로 데이터')
    assert ce.validate_tags(["제로데이", "망분리"], "other", "제로 데이터 이동 망분리 환경") == ["망분리"]


def test_tag_evidence_excludes_llm_written_korean():
    # QA C3: LLM이 요약에 지어낸 '원격 코드 실행'이 RCE 태그의 근거가 되던 구멍
    item = {"title": "Plugin flaw lets admins read files", "summary": "path traversal", "kind": "vuln"}
    fields = {"title_ko": "플러그인 원격 코드 실행 취약점 공개",
              "summary_ko": "공격자가 **원격 코드 실행**을 할 수 있는 취약점이 공개됐다. "
                            "업체는 보안 패치를 배포했다고 밝혔다.",
              "tags_ko": ["RCE", "원격코드실행"]}
    assert ce.apply_news_fields(item, fields)
    assert "tags_ko" not in item


def test_why_and_cve_desc_reject_english_phrases():
    # QA C12
    assert ce.validate_why("Attackers can exploit this to gain admin access 다.") is None
    assert ce.validate_why("Patch now 했다.") is None
    assert ce.validate_why(GOOD["why_ko"]) == GOOD["why_ko"]
    assert ce.validate_cve_desc("Fortinet FortiOS heap overflow in sslvpnd 취약") is None
    assert ce.validate_cve_desc("Remote code execution in Apache Tomcat 원격") is None
    for d in ("FortiOS 힙 오버플로", "Cisco IOS XE 인증 우회", "Microsoft SharePoint 역직렬화"):
        assert ce.validate_cve_desc(d) == d


def test_region_comes_from_rewrite_output_only():
    # QA D6: 사건지 pill은 재작성 출력의 region. 값이 이상하면 생략
    item = {"title": "x", "summary": GOOD_SOURCE, "kind": "incident"}
    assert ce.apply_news_fields(item, dict(GOOD, region="해외"))
    assert item["region"] == "해외"
    assert ce.apply_news_fields(item, dict(GOOD, region="미국"))
    assert "region" not in item
    assert ce.apply_news_fields(item, {k: v for k, v in GOOD.items() if k != "region"})
    assert "region" not in item


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
        {"id": "a", "title": "Yellow umbrella breach", "summary": GOOD_SOURCE,
         "kind": "incident", "url": "u1"},
        # 사서 문안도 영어 — 재작성 실패 시 대체 문안도 검증에 걸려 빠져야 한다
        {"id": "b", "title": "Policy and Disclosure: 2026 Edition", "url": "u2",
         "title_ko": "Policy and Disclosure: 2026 Edition"},
    ]
    cve = [{"id": "c", "title": "ICSA-26-321-08 Siemens SIMATIC", "lane": "cve"}]
    kept_news, kept_cve = ce.rewrite(news, cve, fetch=False)
    assert [n["id"] for n in kept_news] == ["a"]
    assert kept_news[0]["term_ko"].startswith("크리덴셜 스터핑")
    assert kept_news[0]["tags_ko"] == ["개인정보유출사고", "공제회", "국내사고"]
    assert kept_news[0]["region"] == "국내"
    assert kept_cve[0]["title_ko"] == "Siemens SIMATIC 인증 우회 취약점"


def test_rewrite_failure_falls_back_to_valid_draft(monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    news = [dict(GOOD, id="a", title="x", url="u", kind="incident",
                 term_ko="금융보안원 — 금융권 보안 기관")]
    kept, _ = ce.rewrite(news, [], fetch=False)
    assert kept[0]["title_ko"] == GOOD["title_ko"]
    assert kept[0]["term_ko"] is None  # 사서 초안의 기관명 용어는 버려진다
    assert "region" not in kept[0]     # 사서 문안에는 사건지 판단이 없다


def test_google_news_headline_list_is_not_a_valid_summary():
    raw = ("금융위, '해킹 사고' 금융보안원 현장 점검 MBC 뉴스 '해킹사고' 금융보안원 찾은 "
           "신진창 부위원장 머니투데이 금융위, 금융보안원 침해사고에 유감 표명 Chosunbiz")
    assert ce.validate_summary(raw) is None


# --- 2026-11-20 QA 실행 뒤 보강 ----------------------------------------------

def test_term_latin_gloss_in_parentheses_is_stripped():
    t = ce.validate_term("공급망 공격 (Supply Chain Attack) — 신뢰된 제3자를 통해 최종 대상을 공격")
    assert t == "공급망 공격 — 신뢰된 제3자를 통해 최종 대상을 공격"


def test_term_must_appear_in_card_text():
    assert ce.term_in_card("공급망 공격 — 정의", "제목", "**공급망공격**으로 피해가 났다.")
    assert not ce.term_in_card("복원력 — 공격 뒤 서비스를 복구하는 능력",
                               "영국 금융당국 사이버보안 책임 명확화",
                               "금융기관의 사이버 위험 관리를 경영 책임으로 정했다.")


def test_rewrite_splits_news_into_chunks_and_merges(monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "x")
    prompts = []

    def fake_run(args, prompt, timeout):
        prompts.append(prompt)
        start = prompt.index("항목:\n") + len("항목:\n")
        nums = [p["n"] for p in json.loads(prompt[start:])]
        items = {str(n): dict(GOOD) for n in nums}
        return SimpleNamespace(returncode=0, stdout=json.dumps(
            {"result": json.dumps({"items": items})}))

    monkeypatch.setattr(librarian, "_run_claude_json", fake_run)
    news = [{"id": str(i), "title": "Yellow umbrella breach", "summary": GOOD_SOURCE,
             "kind": "incident", "url": f"u{i}"} for i in range(7)]
    kept, _ = ce.rewrite(news, [], fetch=False)
    assert len(prompts) == 3          # 7건을 3건씩 나눠 세 번
    assert len(kept) == 7
    assert all(k["region"] == "국내" for k in kept)


def test_entity_tags_are_dropped():
    # 2026-11-23 QA 실행: NCIC, NSANet, 롯데카드가 태그 pill로 나갔다
    ev = "NCIC NSANet 롯데카드 개인정보 유출 사고 과징금 프롬프트 인젝션"
    assert ce.validate_tags(["NCIC", "개인정보유출"], "incident", ev) == ["개인정보유출"]
    assert ce.validate_tags(["NSANet"], "incident", ev) == []
    assert ce.validate_tags(["롯데카드", "과징금"], "policy", ev) == ["과징금"]
