"""dedup.py 순수 로직 단위 테스트 — 네트워크·상태파일 무의존."""
from datetime import datetime, timedelta, timezone

import dedup


def _state() -> dict:
    return {"alerted_cves": {}, "recent_titles": []}


def test_extract_cves_case_and_length():
    text = "cve-2026-1234 and CVE-2026-1234567 but not CVE-26-1"
    assert dedup.extract_cves(text) == {"CVE-2026-1234", "CVE-2026-1234567"}


def test_cve_subset_rule():
    # 언급된 CVE 전부가 기발송이어야 중복 — 새 CVE 하나라도 있으면 새 소식
    state = _state()
    dedup.record_alerted({"title": "Patch CVE-2026-1111"}, state)
    assert dedup.is_cross_duplicate({"title": "Vendor fixes CVE-2026-1111"}, state)
    assert not dedup.is_cross_duplicate(
        {"title": "CVE-2026-1111 chained with CVE-2026-2222"}, state)


def test_title_jaccard_duplicate():
    state = _state()
    dedup.record_alerted({"title": "롯데카드 해킹 사고 297만명 정보 유출"}, state)
    # 매체만 다른 같은 사건 헤드라인(토큰 대부분 겹침) → 중복
    assert dedup.is_cross_duplicate(
        {"title": "롯데카드 해킹 297만명 정보 유출 사고"}, state)
    # 무관한 제목 → 통과
    assert not dedup.is_cross_duplicate(
        {"title": "OpenSSL 신규 릴리스 3.6 발표"}, state)


def test_title_jaccard_boundary():
    # 임계값 0.6 경계 직접 검증 — 합성 토큰으로 유사도를 정확히 제어한다.
    # 임계가 바뀌면(0.6→0.8 등) 이 테스트가 깨져 회귀를 드러낸다.
    state = _state()
    dedup.record_alerted({"title": "alpha bravo charlie delta echo"}, state)
    # 교집합 4, 합집합 6 → 4/6 ≈ 0.667 ≥ 0.6 → 중복
    assert dedup.is_cross_duplicate(
        {"title": "alpha bravo charlie delta foxtrot"}, state)
    # 교집합 3, 합집합 7 → 3/7 ≈ 0.429 < 0.6 → 통과
    assert not dedup.is_cross_duplicate(
        {"title": "alpha bravo charlie golf hotel"}, state)


def test_prune_ttl():
    state = _state()
    now = datetime.now(timezone.utc)
    old = (now - timedelta(days=91)).isoformat()
    fresh = now.isoformat()
    state["alerted_cves"] = {"CVE-2020-0001": old, "CVE-2026-0001": fresh}
    state["recent_titles"] = [
        {"t": "old title", "d": (now - timedelta(days=8)).isoformat()},
        {"t": "fresh title", "d": fresh},
        {"t": "garbage date", "d": "not-a-date"},
    ]
    dedup.prune_dedup_state(state, now=now)
    assert set(state["alerted_cves"]) == {"CVE-2026-0001"}
    assert [e["t"] for e in state["recent_titles"]] == ["fresh title"]


def test_is_similar_event_cve_intersection_and_title_ko():
    a = {"title": "Exploit for CVE-2026-9999 in the wild"}
    b = {"title": "완전히 다른 제목", "summary": "CVE-2026-9999 악용 확인"}
    assert dedup.is_similar_event(a, b)
    # 국내·해외 교차 보도 — 사서 번역(title_ko)끼리 비교
    c = {"title": "Massive breach at ACME", "title_ko": "ACME 대규모 유출 사고 발생"}
    d = {"title": "ACME hit by breach", "title_ko": "ACME 유출 사고 대규모 발생"}
    assert dedup.is_similar_event(c, d)


def test_is_similar_event_hermes_no19_regression():
    # 2026-07-26 NO.19 실측 중복 카드 2장(BleepingComputer·THN). 자카드는
    # 영문 0.4·국문 0.4(조사 차이)로 둘 다 미달이었다
    a = {
        "title": "Hermes AI agent used to automate attack on Thai finance ministry",
        "title_ko": "Hermes AI 에이전트, 태국 재무부 침해 공격 자동화",
    }
    b = {
        "title": (
            "Hacker runs Hermes AI agent unattended for post exploitation "
            "at Thai finance ministry"
        ),
        "title_ko": "Hermes AI 에이전트로 태국 재무부 침입",
    }
    assert dedup.is_similar_event(a, b)


def test_strip_josa_keeps_short_nouns_intact():
    # 2음절 명사가 조사로 오인돼 잘리면 안 된다
    assert dedup._normalize_title("평가 정의 국가 증가 결과") == "평가 정의 국가 증가 결과"
    assert dedup._normalize_title("에이전트로 데이터를 기업의") == "에이전트 데이터 기업"


def test_is_similar_event_containment_needs_strong_overlap():
    # 서로 다른 사건 — 토큰 4개가 겹쳐도 포함률(4/7)이 낮아 중복 아님
    a = {"title": "Clop ransomware targets Windchill FlexPLM in data theft attacks"}
    b = {"title": "Clop ransomware data theft victims named on leak site today"}
    assert not dedup.is_similar_event(a, b)
