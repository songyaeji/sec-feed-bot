"""소스와 사서 입력 컷 테스트(QA D1~D5, 2026-11-20). 네트워크는 전부 모킹.

고정하는 계약:
- 개인정보위 보도자료 크롤러: 목록 파싱, 키워드와 신선도 거르기, 처음 보는
  항목만 상세 요청(detail_limit 상한)
- 구글뉴스 항목: source는 설정 이름, outlet은 실제 매체명
- 과기정통부: body_unavailable 표시와 부제 요약
- KISA 보도자료: https 링크, 날짜 파싱
- 구글뉴스 대리 소스는 기관 가중치를 받지 않는다
- 소스당 상한, 같은 사건 묶기, 사서 입력 컷
- 규칙 분류(사서 실패 경로)
"""
import os
import sys
from datetime import datetime, timezone
from unittest import mock

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import digest_select  # noqa: E402
from sources import keywords, pipc, rss  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures")
NOW = datetime(2026, 11, 20, 3, 0, tzinfo=timezone.utc)


def _read(name: str) -> bytes:
    with open(os.path.join(FIX, name), "rb") as f:
        return f.read()


def _resp(body: bytes, status: int = 200) -> requests.Response:
    r = requests.Response()
    r.status_code = status
    r._content = body
    r.encoding = "utf-8"
    return r


class _FixedNow(datetime):
    @classmethod
    def now(cls, tz=None):
        return NOW if tz is not None else NOW.replace(tzinfo=None)


# --- 키워드 필터 ---------------------------------------------------------------

def test_keywords_ascii_word_boundary():
    assert keywords.match_any("개인정보위, AI 프라이버시 협력", ["AI"])
    assert not keywords.match_any("email said again", ["ai"])
    assert keywords.match_any("과징금 부과", ["과징금"])
    assert not keywords.match_any("", ["유출"])


# --- 개인정보위 보도자료 크롤러 -------------------------------------------------

def test_pipc_parse_list():
    rows = pipc.parse_list(_read("pipc_list.html").decode("utf-8"),
                           "https://pipc.go.kr/")
    assert [r["ntt"] for r in rows] == ["12660", "12648", "12644", "11000"]
    first = rows[0]
    # 새 글 표시 N은 제목에서 빠진다
    assert first["title"] == "개인정보위, Java 보안 취약점 관련 개인정보 대량 유출 예방조치 당부"
    assert first["url"] == ("https://pipc.go.kr/np/cop/bbs/selectBoardArticle.do"
                            "?bbsId=BS074&mCode=C020010000&nttId=12660")
    assert first["published"].startswith("2026-11-18")
    # HTML 엔티티는 풀린다
    assert rows[2]["title"].startswith("‘내 개인정보를")


def test_pipc_parse_detail():
    text = pipc.parse_detail(_read("pipc_detail.html").decode("utf-8"))
    assert text.startswith("- Java 버전 확인 후 보안 취약점 긴급 조치")
    assert "유출 예방을 위한 보호조치를 당부했다" in text
    assert "이하 전문 참조" not in text
    assert pipc.parse_detail("<html>본문 칸 없음</html>") == ""


def _pipc_get(calls):
    def fake_get(url, **kw):
        calls.append(url)
        if "selectBoardList" in url:
            return _resp(_read("pipc_list.html"))
        return _resp(_read("pipc_detail.html"))
    return fake_get


def test_pipc_fetch_filters_and_details():
    cfg = {"name": "개인정보보호위원회 보도자료", "url": pipc.DEFAULT_URL,
           "keywords": ["유출", "제재"], "max_age_days": 14, "detail_limit": 5}
    state = {"seen": {"pipc:BS074:12648": "2026-11-12T00:00:00+00:00"}}
    calls: list[str] = []
    with mock.patch.object(pipc.requests, "get", _pipc_get(calls)), \
            mock.patch.object(pipc, "datetime", _FixedNow), \
            mock.patch.object(pipc, "DETAIL_INTERVAL", 0):
        items = pipc.fetch(cfg, state, {})
    # 공모전(키워드 밖)과 2026-01 항목(신선도 밖)은 빠진다
    assert [it["id"] for it in items] == ["pipc:BS074:12660", "pipc:BS074:12648"]
    assert items[0]["source"] == "개인정보보호위원회 보도자료"
    assert items[0]["summary"].startswith("- Java 버전 확인")
    # 이미 본 항목은 상세를 받지 않는다 — 목록 1회 + 상세 1회
    assert items[1]["summary"] == ""
    assert len(calls) == 2


def test_pipc_detail_limit_and_failure():
    cfg = {"url": pipc.DEFAULT_URL, "max_age_days": False, "detail_limit": 1}
    calls: list[str] = []
    with mock.patch.object(pipc.requests, "get", _pipc_get(calls)), \
            mock.patch.object(pipc, "DETAIL_INTERVAL", 0):
        items = pipc.fetch(cfg, {"seen": {}}, {})
    assert len(items) == 4
    assert sum(1 for it in items if it["summary"]) == 1
    assert len(calls) == 2

    def broken_detail(url, **kw):
        if "selectBoardList" in url:
            return _resp(_read("pipc_list.html"))
        raise requests.ConnectionError("reset")
    with mock.patch.object(pipc.requests, "get", broken_detail), \
            mock.patch.object(pipc, "DETAIL_INTERVAL", 0):
        items = pipc.fetch(cfg, {"seen": {}}, {})
    # 상세 실패는 제목만으로 싣는다
    assert len(items) == 4 and items[0]["summary"] == ""


# --- RSS: 구글뉴스 매체명, 과기정통부, KISA -------------------------------------

def _rss_items(fixture: str, cfg: dict) -> list[dict]:
    with mock.patch.object(rss.requests, "get",
                           lambda url, **kw: _resp(_read(fixture))):
        return rss.fetch(cfg, {}, {"default_max_age_days": False})


def test_google_news_outlet_field():
    items = _rss_items("gn_rss.xml", {"name": "금융보안원", "url": "https://news.google.com/rss/search?q=x",
                                      "max_age_days": False})
    assert len(items) == 2
    tagged, untagged = items
    # source는 설정 이름(가중치와 설정 조회용), outlet은 실제 매체명(카드 출처용)
    assert tagged["source"] == "금융보안원"
    assert tagged["outlet"] == "MBC 뉴스"
    assert tagged["title"] == "금융위, '해킹 사고' 금융보안원 현장 점검"
    # <source> 태그가 없으면 제목 꼬리 " - 매체명"을 쓴다
    assert untagged["outlet"] == "비즈워치"
    assert untagged["title"] == "금융보안원 침해사고 후속 조치"
    assert digest_select.is_news_proxy(tagged)


def test_direct_feed_has_no_outlet():
    items = _rss_items("kisa_rss.xml", {"name": "KISA 보도자료", "url": "https://www.kisa.or.kr/rss/402",
                                        "https_links": True, "max_age_days": False})
    assert all("outlet" not in it for it in items)
    assert not any(digest_select.is_news_proxy(it) for it in items)


def test_kisa_https_links_and_date():
    items = _rss_items("kisa_rss.xml", {"name": "KISA 보도자료", "url": "https://www.kisa.or.kr/rss/402",
                                        "https_links": True, "max_age_days": False,
                                        "keywords": ["보안"]})
    assert len(items) == 1  # "법적 문제 해법" 항목은 키워드 밖
    it = items[0]
    assert it["url"] == "https://www.kisa.or.kr/402/form?postSeq=2657"
    assert it["published"].startswith("2026-11-11")
    assert it["summary"] == ""


def test_msit_body_unavailable_and_subtitle():
    items = _rss_items("msit_rss.xml", {"name": "과기정통부 보도자료",
                                        "url": "https://www.msit.go.kr/user/rss/rss.do?bbsSeqNo=94",
                                        "body_unavailable": True, "max_age_days": False})
    assert len(items) == 1
    it = items[0]
    assert it["body_unavailable"] is True
    assert it["published"].startswith("2026-11-18")
    assert it["summary"].startswith("- 자바 버전과 실행환경 확인")
    assert "&nbsp;" not in it["summary"]
    assert "hwpjson" not in it["summary"]


def test_body_unavailable_off_by_default():
    items = _rss_items("msit_rss.xml", {"name": "x", "url": "https://example.com/rss",
                                        "max_age_days": False})
    assert "body_unavailable" not in items[0]


# --- 순위 점수 ------------------------------------------------------------------

CFG = {
    "source_weights": {"개인정보보호위원회": 50, "KISA 보도자료": 50},
    "news_proxy_weight": 0,
}


def test_proxy_does_not_get_institution_weight():
    proxy = {"source": "개인정보보호위원회", "category": "news",
             "url": "https://news.google.com/rss/articles/abc"}
    official = {"source": "개인정보보호위원회", "category": "news",
                "url": "https://pipc.go.kr/x"}
    assert digest_select._rank_score(proxy, CFG) == 0
    assert digest_select._rank_score(official, CFG) == 50
    assert not digest_select.is_news_proxy({"url": "not a url"})
    assert not digest_select.is_news_proxy({})


def test_kind_bonus_uses_librarian_kind_first():
    cfg = {"kind_rank_bonus": {"incident": 80, "vuln": -60, "other": -80}}
    item = {"source": "X", "title": "Acme patches flaw CVE-2026-1234"}
    assert digest_select._rank_score(item, cfg) == -60
    item["kind"] = "incident"
    assert digest_select._rank_score(item, cfg) == 80
    item["kind"] = ["bad"]  # LLM 출력 타입 불량은 규칙 분류로
    assert digest_select._rank_score(item, cfg) == -60


# --- 소스당 상한, 같은 사건 묶기, 사서 입력 컷 ---------------------------------

def _it(i, source, title=None, url=None):
    # 기본 제목은 항목마다 토큰이 전부 달라 같은 사건으로 묶이지 않는다
    return {"id": str(i), "source": source, "title": title or f"t{i}a t{i}b t{i}c",
            "url": url or f"https://example.com/{source}/{i}"}


def test_cap_per_source_limits_and_backfills():
    ranked = [_it(i, "A") for i in range(5)] + [_it(10, "B"), _it(11, "C")]
    sel, over = digest_select.cap_per_source(ranked, 2, 4)
    assert [it["id"] for it in sel] == ["0", "1", "10", "11"]
    assert [it["id"] for it in over] == ["2", "3", "4"]
    # 상한으로 limit을 못 채우면 순위순으로 더 채운다
    sel, over = digest_select.cap_per_source(ranked, 1, 5)
    assert [it["id"] for it in sel] == ["0", "1", "2", "10", "11"]
    assert [it["id"] for it in over] == ["3", "4"]


def test_cap_per_source_zero_cap_is_plain_cut():
    ranked = [_it(i, "A") for i in range(3)]
    sel, over = digest_select.cap_per_source(ranked, 0, 2)
    assert [it["id"] for it in sel] == ["0", "1"] and [it["id"] for it in over] == ["2"]


def test_cap_counts_proxy_and_official_separately():
    gn = [_it(i, "금융보안원", url=f"https://news.google.com/rss/articles/{i}") for i in range(3)]
    official = [_it(9, "금융보안원", url="https://www.fsec.or.kr/bbs/detail?bbsNo=1")]
    sel, _ = digest_select.cap_per_source(gn + official, 2, 3)
    assert [it["id"] for it in sel] == ["0", "1", "9"]


def test_group_same_event_keeps_top_ranked():
    ranked = [
        _it(1, "A", "Acme breach exposes 10 million customer records"),
        _it(2, "B", "Acme breach exposes 10 million customer records, company says"),
        _it(3, "C", "Unrelated ransomware attack on hospital"),
    ]
    reps, grouped = digest_select.group_same_event(ranked)
    assert [it["id"] for it in reps] == ["1", "3"]
    assert [it["id"] for it in grouped] == ["2"]


def test_librarian_cut_cap_decay_and_overflow():
    ranked = [_it(i, "A") for i in range(4)] + [_it(10, "B"), _it(11, "B")]
    cfg = {"librarian_news_cap": 4, "librarian_source_cap": 2,
           "librarian_source_decay": 100}
    sel, over = digest_select.librarian_cut(ranked, cfg)
    assert sorted(it["id"] for it in sel) == ["0", "1", "10", "11"]
    # 감점으로 같은 소스가 번갈아 앞에 선다(점수 동점이면 입력 순서)
    assert [it["source"] for it in sel] == ["A", "B", "A", "B"]
    assert [it["id"] for it in over] == ["2", "3"]


def test_librarian_cut_grouped_go_to_overflow_in_rank_order():
    ranked = [
        _it(1, "A", "Acme breach exposes 10 million customer records"),
        _it(2, "B", "Acme breach exposes 10 million customer records, company says"),
        _it(3, "C", "Unrelated ransomware attack on hospital"),
        _it(4, "D", "Another story about phishing kits"),
    ]
    sel, over = digest_select.librarian_cut(ranked, {"librarian_news_cap": 2})
    assert [it["id"] for it in sel] == ["1", "3"]
    assert [it["id"] for it in over] == ["2", "4"]


# --- 규칙 분류(사서 실패 경로) --------------------------------------------------

def _kind(title, summary="", source="X", url="https://example.com/a", config=None):
    return digest_select.classify_kind_fallback(
        {"title": title, "summary": summary, "source": source, "url": url}, config)


def test_classify_vuln():
    assert _kind("Drupal patches critical RCE flaw, warns exploits may surface") == "vuln"
    assert _kind("CVE-2026-12345 (CVSS 9.8)") == "vuln"
    assert _kind("과기정통부, 자바 보안 취약점 관련 긴급 점검 및 보안조치 당부") == "vuln"


def test_classify_incident():
    assert _kind("노란우산 개인정보 36만건 유출 확인") == "incident"
    assert _kind("Hackers steal data of 1.6 million SBC Medical Group customers") == "incident"
    assert _kind("Cyberattack hits Norwegian energy giant Equinor") == "incident"
    # "유출시"의 "출시"는 홍보로 보지 않는다
    assert _kind("정부기관서 개인정보 유출시 기관장도 책임") == "incident"


def test_classify_policy():
    assert _kind("Italian regulator fines Meta $886 million") == "policy"
    assert _kind("금융권 IT자산 관리 의무화…대형 금융사 보안점검 연 2회로") == "policy"
    assert _kind("쿠팡 유출 과징금 4236억 유지") == "policy"


def test_classify_institution():
    assert _kind("KISA, 클라우드 보안 가이드 발간") == "institution"
    assert _kind("NCSC publishes new guidance for critical organisations") == "institution"
    assert _kind("AI 보안위협 대응 매뉴얼") == "institution"


def test_classify_other():
    assert _kind("2026년 10월 외국인 증권투자 동향") == "other"
    assert _kind("SM솔루션즈, 운영서버 취약점 관리 솔루션 출시") == "other"
    assert _kind("[포토] 한일 개인정보보호위원장") == "other"
    assert _kind("[기고] AI 시대 개인정보 유출, 경계 재정비해야") == "other"
    assert _kind("대한민국 차세대 보안 리더, 국제 해킹대회 우승!") == "other"
    # 홍보 표지가 있어도 사고 핵심어가 있으면 사고로 본다
    assert _kind("OO사 신제품 출시 직후 고객정보 유출") == "incident"


def test_classify_institution_source_default():
    cfg = {"institution_sources": ["KISA 보도자료"]}
    # 제목 신호가 없을 때 기관 원문은 기관 발표, 요약의 부수 언급은 보지 않는다
    assert _kind("인공지능 안전 지킴이 출범", "보안 취약점 제보 체계", source="KISA 보도자료",
                 config=cfg) == "institution"
    assert _kind("인공지능 안전 지킴이 출범", "보안 취약점 제보 체계",
                 config=cfg) == "vuln"
    # 같은 이름이라도 구글뉴스 대리 소스는 기본값 대상이 아니다
    assert _kind("인공지능 안전 지킴이 출범", source="KISA 보도자료",
                 url="https://news.google.com/rss/articles/x", config=cfg) == "other"
    assert digest_select.classify_kind_fallback({}) == "other"


def test_classify_returns_known_kinds_only():
    for title in ("", "random words", "breach", "law", "CVE-2026-0001"):
        assert _kind(title) in digest_select.KNOWN_KINDS
