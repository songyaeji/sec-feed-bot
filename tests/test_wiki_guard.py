"""위키 기록 검증(wiki_guard)과 INDEX 재생성(wiki_index) 테스트 — 임시 위키로.

2026-11-20 점검에서 확인된 구멍을 고정한다:
  - 사서가 new·update로 답하고 페이지·타임라인을 안 쓴 경우(SCKit, FBI 북한)
  - 규약 밖 파일(wiki/librarian_verdict.json)을 모델이 임의 생성
  - [[slug]] 링크가 Obsidian에서 안 열림(파일명은 YYYY-MM-slug)
  - INDEX 중복 줄·누락 페이지·없는 파일 줄
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wiki_guard  # noqa: E402
import wiki_index  # noqa: E402

PAGE = """---
slug: fsic-breach
first_seen: 2026-11-11
tags: [금융보안원]
cves: []
---

**금융보안원** 상시평가시스템이 해킹됐다. 금융사 자료가 유출됐다.

## 타임라인

- 2026-11-11 [데일리시큐](https://a/1) — 최초 보도
- 2026-11-19 [뉴스](https://a/3) — 원인 조사

## 관련
[[korea-fintech-breach-wave]]
"""


@pytest.fixture
def wiki(tmp_path, monkeypatch):
    topics = tmp_path / "topics"
    topics.mkdir()
    (topics / "2026-11-fsic-breach.md").write_text(PAGE, encoding="utf-8")
    (topics / "2026-11-korea-fintech-breach-wave.md").write_text(
        "---\nslug: korea-fintech-breach-wave\nfirst_seen: 2026-11-07\n---\n\n금융권 연쇄 침해.\n\n"
        "## 타임라인\n\n- 2026-11-07 [x](https://b/1) — 47만건\n\n## 관련\n",
        encoding="utf-8")
    (tmp_path / "INDEX.md").write_text(
        "# 보안동향 위키 인덱스\n\n"
        "- [fsic-breach](topics/2026-11-fsic-breach.md) 금보원 해킹 기존 요약 (최종갱신일: 2026-11-18)\n"
        "- [fsic-breach](topics/2026-11-fsic-breach.md) 중복 줄 (최종갱신일: 2026-11-12)\n"
        "- [ghost](topics/2026-07-ghost.md) 없는 파일 (최종갱신일: 2026-11-01)\n",
        encoding="utf-8")
    for mod in (wiki_guard, wiki_index):
        monkeypatch.setattr(mod, "TOPICS_DIR", str(topics))
        monkeypatch.setattr(mod, "WIKI_DIR", str(tmp_path))
    monkeypatch.setattr(wiki_index, "WIKI_INDEX_PATH", str(tmp_path / "INDEX.md"))
    monkeypatch.setattr(wiki_index, "WIKI_INDEX_ARCHIVE_PATH", str(tmp_path / "INDEX-archive.md"))
    return tmp_path


def test_missing_page_is_created(wiki):
    item = {"id": "s", "title": "New worm-like SCKit malware targets MSPs",
            "title_ko": "SCKit 웜형 악성코드 MSP 표적", "summary_ko": "**SCKit**이 MSP를 노렸다.",
            "url": "https://bleepingcomputer.com/sckit", "source": "BleepingComputer",
            "tags_ko": ["웜형악성코드", "MSP"]}
    stats = wiki_guard.ensure_recorded(
        [item], {"s": {"action": "new", "kind": "incident", "topic": "sckit-msp-worm"}}, "2026-11-16")
    assert stats["created"] == 1
    text = (wiki / "topics" / "2026-11-sckit-msp-worm.md").read_text(encoding="utf-8")
    assert "slug: sckit-msp-worm" in text
    assert "- 2026-11-16 [BleepingComputer](https://bleepingcomputer.com/sckit) — SCKit 웜형 악성코드 MSP 표적" in text


def test_missing_timeline_line_is_inserted_in_date_order(wiki):
    item = {"id": "f", "title_ko": "금융보안원 경찰 수사 착수", "url": "https://a/2", "source": "뉴스"}
    stats = wiki_guard.ensure_recorded(
        [item], {"f": {"action": "update", "kind": "incident", "topic": "fsic-breach"}}, "2026-11-14")
    assert stats["appended"] == 1
    text = (wiki / "topics" / "2026-11-fsic-breach.md").read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.startswith("- 2026")]
    assert [ln[2:12] for ln in lines] == ["2026-11-11", "2026-11-14", "2026-11-19"]
    assert text.index("## 관련") > text.index("2026-11-19")


def test_recorded_item_is_left_alone(wiki):
    before = (wiki / "topics" / "2026-11-fsic-breach.md").read_text(encoding="utf-8")
    item = {"id": "f", "url": "https://a/1"}
    stats = wiki_guard.ensure_recorded(
        [item], {"f": {"action": "update", "kind": "incident", "topic": "fsic-breach"}}, "2026-11-20")
    after = (wiki / "topics" / "2026-11-fsic-breach.md").read_text(encoding="utf-8")
    assert stats["appended"] == 0
    # 확인한 페이지는 링크만 파일명으로 정리된다
    assert after == before.replace("[[korea-fintech-breach-wave]]",
                                   "[[2026-11-korea-fintech-breach-wave]]")


def test_vuln_and_no_wiki_verdicts_are_not_paged(wiki):
    item = {"id": "v", "title": "Elecbrakes", "url": "https://cisa/x"}
    stats = wiki_guard.ensure_recorded(
        [item], {"v": {"action": "new", "kind": "vuln", "topic": "elecbrakes"}}, "2026-11-20")
    assert stats["checked"] == 0
    assert not (wiki / "topics" / "2026-11-elecbrakes.md").exists()


def test_bad_slug_gets_fallback(wiki):
    item = {"id": "k", "title": "국내 대학 해킹", "url": "https://k/1", "title_ko": "대학 해킹"}
    verdicts = {"k": {"action": "new", "kind": "incident", "topic": "../../etc/passwd"}}
    wiki_guard.ensure_recorded([item], verdicts, "2026-11-20")
    assert verdicts["k"]["topic"].startswith("event-")
    assert len(list((wiki / "topics").glob("2026-11-event-*.md"))) == 1


def test_stray_files_created_during_run_are_removed(wiki):
    before = wiki_guard.snapshot()
    (wiki / "old_stray.json").write_text("{}", encoding="utf-8")  # 실행 전부터 있던 것 아님
    before_with_old = before | {"keep_me.json"}
    (wiki / "keep_me.json").write_text("{}", encoding="utf-8")
    (wiki / "topics" / "2026-11-new-page.md").write_text("x", encoding="utf-8")
    removed = wiki_guard.remove_stray(before_with_old)
    assert removed == ["old_stray.json"]
    assert (wiki / "keep_me.json").exists()
    assert (wiki / "topics" / "2026-11-new-page.md").exists()


def test_migrate_links_is_idempotent(wiki):
    assert wiki_guard.migrate_links() == 1
    assert wiki_guard.migrate_links() == 0


def test_rebuild_index_dedupes_and_archives(wiki):
    from datetime import datetime, timedelta, timezone
    now = datetime(2026, 11, 20, tzinfo=timezone(timedelta(hours=9)))
    recent, old = wiki_index.rebuild_index(10, now=now)
    index = (wiki / "INDEX.md").read_text(encoding="utf-8")
    archive = (wiki / "INDEX-archive.md").read_text(encoding="utf-8")
    assert (recent, old) == (1, 1)
    assert index.count("2026-11-fsic-breach.md") == 1
    assert "금보원 해킹 기존 요약 (최종갱신일: 2026-11-19)" in index  # 기존 문구 유지, 날짜는 타임라인 최신
    assert "ghost" not in index and "ghost" not in archive        # 없는 파일 줄 제거
    assert "2026-11-korea-fintech-breach-wave.md) 금융권 연쇄 침해" in archive  # 줄 없던 페이지 보충
