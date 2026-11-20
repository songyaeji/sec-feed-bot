"""2026-11-20 개편 결정적 가드 테스트 — 태그 단어 경계, 한국어 fatal,
CVE 코너 구성, 발행 원장 병합."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cardgen  # noqa: E402
import merge_state  # noqa: E402
import preflight  # noqa: E402
import tagger  # noqa: E402

# config.yaml tags 표기: 전부 대문자 약어는 대소문자 구분
RULES = {"RCE": ["RCE", "remote code execution", "원격 코드"], "APT": ["APT"], "랜섬웨어": ["랜섬웨어"],
         "제로데이": ["zero-day", "0-day", "in the wild"], "AI": ["LLM", "deepfake"],
         "금융": ["페이", "ATM"]}


# --- tagger: 공용 매처(text_rules.keyword_matcher) ----------------------------

def test_english_keyword_does_not_match_inside_words():
    item = tagger.tag_item({"title": "Open source resource exhausts force", "summary": "chapter capture adapt"}, RULES)
    assert item["tags"] == []


def test_english_keyword_matches_whole_word_and_korean_substring():
    item = tagger.tag_item({"title": "Critical RCE in router", "summary": "랜섬웨어가 확산"}, RULES)
    assert item["tags"] == ["RCE", "랜섬웨어"]
    assert tagger.tag_item({"title": "APT29 campaign"}, RULES)["tags"] == ["APT"]  # 그룹명 번호 허용
    assert tagger.tag_item({"title": "APT-group linked"}, RULES)["tags"] == ["APT"]


# QA C10 경계 사례 (키워드, 텍스트, 기대). 실측 26/27, 남은 1건은 소문자 llm-based
MATCHER_CASES = [
    ("LLM", "Attackers abused LLMs to write malware", True),
    ("zero-day", "Google fixes two zero-days in Chrome", True),
    ("zero-day", "a zero day in Chrome", True),
    ("0-day", "two 0-days chained", True),
    ("deepfake", "deepfakes used in CEO fraud", True),
    ("APT", "APT41 targeted telecoms", True),
    ("APT", "run apt-get install openssl", False),
    ("APT", "sudo apt install curl to patch", False),
    ("RCE", "open source resource exhaustion", False),
    ("RCE", "two RCEs fixed in Patch Tuesday", True),
    ("prompt injection", "prompt-injection attack on Copilot", True),
    ("phishing", "spear-phishing emails", True),
    ("ATM", "ATMs hit by jackpotting", True),
    ("ATM", "atm_tc_enqueue null deref", False),
    ("C2", "C2C marketplace for goods", False),
    ("C2", "beacon to C2 server", True),
    ("in the wild", "in-the-wild exploitation confirmed", True),
    ("페이", "웹 페이지 변조 공격", False),
    ("페이", "딥페이크 영상과 인터페이스 결함", False),
    ("페이", "카카오페이 정보 유출", True),
    ("원격 코드", "치명적 원격코드실행 위험", True),
    ("제로데이", "제로 데이터 이동", False),
]


def test_shared_matcher_boundary_cases():
    import text_rules
    for kw, text, expected in MATCHER_CASES:
        assert text_rules.keyword_matcher(kw)(text) is expected, (kw, text)


def test_tagger_uses_shared_matcher():
    assert tagger.tag_item({"title": "홈페이지 변조, 딥페이크 피해"}, RULES)["tags"] == []
    assert tagger.tag_item({"title": "Zero-Days exploited", "summary": "LLMs abused"},
                           RULES)["tags"] == ["제로데이", "AI"]


def test_config_tag_keywords_use_uppercase_acronyms():
    import yaml
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "config.yaml"), encoding="utf-8") as f:
        tags = yaml.safe_load(f)["tags"]
    for kw in ("LLM", "RCE", "APT", "SWIFT", "ATM"):
        assert any(kw in kws for kws in tags.values()), kw
    assert not any(k in kws for kws in tags.values() for k in ("llm", "rce", "apt", "swift", "atm"))


# --- cardgen: 뉴스 카드 pill (QA C2 태그 폴백 금지, D6 사건지) ---------------

def _news_html(item, regions=None):
    return cardgen._build_news(cardgen._load_fragments(), item, "2026.11.20", n=2,
                               regions=regions or {}, dots="")


def test_news_card_has_no_rule_tag_fallback():
    item = {"title_ko": "관광공사 개인정보 유출", "summary_ko": "요약이다.", "source": "보안뉴스",
            "tags": ["금융"]}
    assert "금융" not in _news_html(item)
    item["tags_ko"] = ["개인정보유출"]
    assert "개인정보유출" in _news_html(item)


def test_news_card_region_pill_comes_from_item_not_source_map():
    item = {"title_ko": "중국 해킹 그룹 외교부 표적", "summary_ko": "요약이다.", "source": "보안뉴스"}
    html_text = _news_html(item, regions={"보안뉴스": "국내"})
    assert "국내" not in html_text and "해외" not in html_text  # 사건지 없으면 생략
    item["region"] = "해외"
    html_text = _news_html(item, regions={"보안뉴스": "국내"})
    assert "해외" in html_text and "국내" not in html_text


# --- preflight: 전면 한국어 fatal --------------------------------------------

def _check(items):
    links = [f"{i}. https://x/{i}" for i in range(1, len(items) + 1)]
    fatal, _ = preflight.check_card_news([b"png"] * 3, links, items, "총평이다.", {})
    return fatal


def test_english_title_is_fatal():
    fatal = _check([{"id": "a", "title": "Policy and Disclosure", "title_ko": "Policy and Disclosure",
                     "summary_ko": "요약이다."}])
    assert any("한국어 제목" in f for f in fatal)


def test_news_without_summary_is_fatal_but_cve_lane_is_not():
    fatal = _check([
        {"id": "n", "title_ko": "노란우산 개인정보 유출"},
        {"id": "c", "title_ko": "Siemens SIMATIC 인증 우회", "lane": "cve"},
    ])
    assert any("한국어 요약 없는 뉴스 1건" in f and "'n'" in f for f in fatal)


def test_korean_cards_pass():
    assert _check([
        {"id": "n", "title_ko": "노란우산 개인정보 유출", "summary_ko": "36만명 정보가 유출됐다."},
        {"id": "c", "title_ko": "Siemens SIMATIC 인증 우회", "lane": "cve"},
    ]) == []


# --- cardgen: CVE 코너 구성 --------------------------------------------------

def test_cve_lane_articles_go_to_cve_corner_in_given_order():
    items = [
        {"id": "n1", "title": "news", "title_ko": "뉴스", "summary_ko": "요약이다."},
        {"id": "v2", "title": "ICSA-26-321-08 Siemens", "lane": "cve"},
        {"id": "v1", "title": "CVE-2026-1111", "cvss": 9.8},
    ]
    top, cve_rest, other_rest = cardgen.plan_cards(items)
    assert [it["id"] for it in top] == ["n1"]
    assert [it["id"] for it in cve_rest] == ["v2", "v1"]
    assert other_rest == []


def test_zero_news_day_has_no_news_cards():
    top, cve_rest, _ = cardgen.plan_cards([{"id": "v", "title": "CVE-2026-2", "cvss": 7.5}])
    assert top == [] and len(cve_rest) == 1


def test_row_id_uses_advisory_number_when_no_cve():
    assert cardgen._row_id({"title": "Elecbrakes", "url": "https://cisa.gov/news/ics-advisories/icsa-26-321-08"}) == "ICSA-26-321-08"
    assert cardgen._row_id({"title": "CVE-2026-12345 in X"}) == "CVE-2026-12345"
    assert cardgen._row_id({"title": "벤더 권고", "url": "https://x"}) == "CVE 미지정"


# --- merge_state: 발행 원장 병합 ---------------------------------------------

def test_merge_state_unions_published_ledger(tmp_path, monkeypatch):
    from datetime import date, timedelta
    today = date.today()
    d1, d2 = (today - timedelta(days=1)).isoformat(), today.isoformat()
    local = [{"date": d2, "url": "https://x/local", "title_ko": "로컬"}]
    remote = [{"date": d1, "url": "https://x/remote", "title_ko": "원격"},
              {"date": d2, "url": "https://www.x/local/", "title_ko": "원격 중복"}]
    pub = tmp_path / "published.json"
    pub.write_text(json.dumps(local, ensure_ascii=False), encoding="utf-8")
    for name in ("SEEN_PATH", "PENDING_PATH", "URGENT_PATH"):
        monkeypatch.setattr(merge_state, name, str(tmp_path / f"{name}.json"))
    monkeypatch.setattr(merge_state, "PUBLISHED_PATH", str(pub))
    monkeypatch.setattr(merge_state, "_load_ref",
                        lambda ref, rel, default: remote if rel == "state/published.json" else default)
    merge_state.main("origin/main")
    merged = json.loads(pub.read_text(encoding="utf-8"))
    assert sorted(e["title_ko"] for e in merged) == ["로컬", "원격"]
    assert pub.read_text(encoding="utf-8").endswith("\n")


# --- LLM 출력 타입 가드: digest 런 중단 방지 ---------------------------------

def test_librarian_chunk_drops_non_dict_verdicts(monkeypatch, tmp_path):
    from types import SimpleNamespace
    import librarian
    payload = json.dumps({"result": json.dumps({"verdicts": {
        "a": "garbage", "b": {"action": "new", "kind": ["incident"]}}})})
    monkeypatch.setattr(librarian, "_write_input", lambda chunk, path: None)
    monkeypatch.setattr(librarian, "_run_claude_json",
                        lambda *a, **k: SimpleNamespace(returncode=0, stdout=payload, stderr=""))
    ws = str(tmp_path)
    assert librarian._run_chunk([], "p", ws) == {"b": {"action": "new", "kind": ["incident"]}}
    payload = json.dumps({"result": json.dumps({"verdicts": ["x"]})})
    monkeypatch.setattr(librarian, "_run_claude_json",
                        lambda *a, **k: SimpleNamespace(returncode=0, stdout=payload, stderr=""))
    assert librarian._run_chunk([], "p", ws) is None


def test_wiki_guard_list_kind_does_not_crash(tmp_path, monkeypatch):
    import wiki_guard
    (tmp_path / "topics").mkdir()
    monkeypatch.setattr(wiki_guard, "TOPICS_DIR", str(tmp_path / "topics"))
    monkeypatch.setattr(wiki_guard, "WIKI_DIR", str(tmp_path))
    item = {"id": "a", "title": "x", "title_ko": "사건 제목", "url": "https://x/a"}
    stats = wiki_guard.ensure_recorded(
        [item], {"a": {"action": "new", "kind": ["incident"], "topic": "some-event"}}, "2026-11-21")
    assert stats["created"] == 1
