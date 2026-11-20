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

RULES = {"RCE": ["rce", "remote code execution"], "APT": ["apt"], "랜섬웨어": ["랜섬웨어"]}


# --- tagger: 영문 키워드 단어 경계 -----------------------------------------

def test_english_keyword_does_not_match_inside_words():
    item = tagger.tag_item({"title": "Open source resource exhausts force", "summary": "chapter capture adapt"}, RULES)
    assert item["tags"] == []


def test_english_keyword_matches_whole_word_and_korean_substring():
    item = tagger.tag_item({"title": "Critical RCE in router", "summary": "랜섬웨어가 확산"}, RULES)
    assert item["tags"] == ["RCE", "랜섬웨어"]
    assert tagger.tag_item({"title": "APT29 campaign"}, RULES)["tags"] == ["APT"]  # 그룹명 번호 허용
    assert tagger.tag_item({"title": "apt-group linked"}, RULES)["tags"] == ["APT"]


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
