"""위키 정비(wiki_guard.maintenance)와 기록 보충 보강 테스트 — 임시 위키로.

2026-11-20 QA(docs/qa/2026-11-20-qa-results.md) E1~E8, F3 회귀를 고정한다:
  - E4 대문자 slug 미검색과 Windows 덮어쓰기, 소문자 rename
  - E5 없는 파일 링크, E6 앵커 링크와 코드 span, 타임라인 하위 줄
  - E7 Obsidian 태그 규칙, E8 확정 병합과 slug 충돌 분리
  - E3 원장 소급 기록, E1 E2 발송분 기록과 kind 정규화, F3 보호 파일 복원
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wiki_guard  # noqa: E402
import wiki_index  # noqa: E402


def page(slug, first_seen, body, tags="[]", cves="[]", timeline="", related=""):
    return (f"---\nslug: {slug}\nfirst_seen: {first_seen}\ntags: {tags}\ncves: {cves}\n---\n\n"
            f"{body}\n\n## 타임라인\n\n{timeline}\n\n## 관련\n{related}")


@pytest.fixture
def wiki(tmp_path, monkeypatch):
    topics = tmp_path / "topics"
    topics.mkdir()
    for mod in (wiki_guard, wiki_index):
        monkeypatch.setattr(mod, "TOPICS_DIR", str(topics))
        monkeypatch.setattr(mod, "WIKI_DIR", str(tmp_path))
    monkeypatch.setattr(wiki_index, "WIKI_INDEX_PATH", str(tmp_path / "INDEX.md"))
    monkeypatch.setattr(wiki_index, "WIKI_INDEX_ARCHIVE_PATH", str(tmp_path / "INDEX-archive.md"))
    monkeypatch.setattr(wiki_guard, "MERGES", {})
    monkeypatch.setattr(wiki_guard, "SLUG_RENAMES", {})
    return tmp_path


def write(wiki, name, text):
    (wiki / "topics" / f"{name}.md").write_text(text, encoding="utf-8")


def read(wiki, name):
    return (wiki / "topics" / f"{name}.md").read_text(encoding="utf-8")


def names(wiki):
    return sorted(p.name[:-3] for p in (wiki / "topics").glob("*.md"))


def case_sensitive_fs(tmp_path) -> bool:
    probe = tmp_path / "CaseProbe"
    probe.write_text("x", encoding="utf-8")
    return not (tmp_path / "caseprobe").exists()


# ------------------------------------------------------------ E4 대소문자

MAC = page("macOS-screen-sharing-auth-bypass", "2026-11-18", "**macOS** 화면 공유 인증 우회 원래 요약.",
           timeline="- 2026-11-18 [NVD](https://nvd/1) — 최초 공개")


def test_mixed_case_page_is_found_not_overwritten(wiki):
    """옛 코드는 slug를 소문자로 바꿔 못 찾고 같은 이름 소문자 파일을 새로 써서
    Windows에서 원래 페이지를 덮어썼다(QA E4 재현)."""
    write(wiki, "2026-11-macOS-screen-sharing-auth-bypass", MAC)
    item = {"id": "x", "url": "https://t/2", "title_ko": "macOS 화면 공유 우회 후속", "source": "T"}
    stats = wiki_guard.ensure_recorded(
        [item], {"x": {"action": "update", "kind": "incident",
                       "topic": "macOS-screen-sharing-auth-bypass"}}, "2026-11-20")
    assert (stats["created"], stats["appended"]) == (0, 1)
    assert names(wiki) == ["2026-11-macOS-screen-sharing-auth-bypass"]
    text = read(wiki, "2026-11-macOS-screen-sharing-auth-bypass")
    assert "원래 요약" in text and "- 2026-11-20 [T](https://t/2) — macOS 화면 공유 우회 후속" in text


def test_find_topic_ignores_case():
    files = {"2026-11-nAble-x-zeroday": "p"}
    assert wiki_guard.find_topic("nable-x-zeroday", files) == "2026-11-nAble-x-zeroday"
    assert wiki_guard.find_topic("NABLE-X-ZERODAY", files) == "2026-11-nAble-x-zeroday"


def test_lowercase_names_renames_file_slug_and_links(wiki):
    write(wiki, "2026-11-macOS-screen-sharing-auth-bypass", MAC)
    write(wiki, "2026-11-other", page("other", "2026-11-19", "다른 사건.",
                                      related="[[macOS-screen-sharing-auth-bypass]]"))
    assert wiki_guard.lowercase_names() == 1
    assert "2026-11-macos-screen-sharing-auth-bypass" in names(wiki)
    assert "slug: macos-screen-sharing-auth-bypass" in read(wiki, "2026-11-macos-screen-sharing-auth-bypass")
    wiki_guard.migrate_links()
    assert "[[2026-11-macos-screen-sharing-auth-bypass]]" in read(wiki, "2026-11-other")
    assert wiki_guard.lowercase_names() == 0


def test_lowercase_merges_case_only_duplicate_on_case_sensitive_fs(wiki):
    if not case_sensitive_fs(wiki):
        pytest.skip("대소문자 무시 파일시스템 — Linux 전용 경로")
    write(wiki, "2026-11-macOS-screen-sharing-auth-bypass", MAC)
    write(wiki, "2026-11-macos-screen-sharing-auth-bypass", page(
        "macos-screen-sharing-auth-bypass", "2026-11-20", "소문자 쪽.",
        timeline="- 2026-11-20 [T](https://t/9) — 후속"))
    assert wiki_guard.lowercase_names() == 1
    assert names(wiki) == ["2026-11-macos-screen-sharing-auth-bypass"]
    text = read(wiki, "2026-11-macos-screen-sharing-auth-bypass")
    assert "https://nvd/1" in text and "https://t/9" in text


def test_create_page_never_overwrites(wiki):
    write(wiki, "2026-11-a-b", "원본")
    files = wiki_guard.topic_files()
    assert wiki_guard._create_page(files, "2026-11-a-b", "새 글") == "2026-11-a-b"
    assert read(wiki, "2026-11-a-b") == "원본"


# ------------------------------------------------------------ E5 E6 링크

def test_links_anchor_alias_missing_and_code(wiki):
    write(wiki, "2026-07-target-page", page("target-page", "2026-07-01", "대상."))
    body = (
        "[[target-page#타임라인]] [[target-page#타임라인|별칭]] [[target-page|보기]]\n"
        "[[no-such-hub]] [[no-such|없는 별칭]] [[#같은 페이지]]\n"
        "`[[target-page]]` 코드 span\n"
        "```\n[[target-page]]\n```\n"
    )
    write(wiki, "2026-07-src", page("src", "2026-07-02", body))
    stats = {}
    assert wiki_guard.migrate_links(stats) == 1
    text = read(wiki, "2026-07-src")
    assert ("[[2026-07-target-page#타임라인]] [[2026-07-target-page#타임라인|별칭]] "
            "[[2026-07-target-page|보기]]") in text
    assert "no-such-hub 없는 별칭 [[#같은 페이지]]" in text
    assert "`[[target-page]]` 코드 span" in text
    assert "```\n[[target-page]]\n```" in text
    assert stats == {"links_relinked": 3, "links_unlinked": 2}
    assert wiki_guard.migrate_links() == 0


def test_timeline_insert_keeps_sub_lines_with_parent():
    text = page("f", "2026-02-24", "요약.", timeline=(
        "- 2026-02-24 [NVD](https://n/1) — 5개 취약점 수정\n"
        "  - CVE-2026-2760: 경계 조건\n"
        "  - CVE-2026-2761: 오류\n"
        "- 2026-03-01 [B](https://n/2) — 후속"))
    out = wiki_guard._insert_timeline(text, "- 2026-02-20 [A](https://n/0) — 앞선 보도")
    section = out.split("## 타임라인\n\n")[1].split("\n\n## 관련")[0].split("\n")
    assert section == [
        "- 2026-02-20 [A](https://n/0) — 앞선 보도",
        "- 2026-02-24 [NVD](https://n/1) — 5개 취약점 수정",
        "  - CVE-2026-2760: 경계 조건",
        "  - CVE-2026-2761: 오류",
        "- 2026-03-01 [B](https://n/2) — 후속",
    ]
    assert "후속\n\n## 관련" in out


# ------------------------------------------------------------ E7 태그

@pytest.mark.parametrize("raw,want", [
    ("Linux kernel", "Linuxkernel"), ("Node.js", "Nodejs"), ("CVSS 10.0", "CVSS10_0"),
    ("C++", "Cpp"), ("Windows·Linux", "Windows-Linux"), (".NET원격처리", "NET원격처리"),
    ("공급망 공격", "공급망공격"), ("2026", ""), ("RaaS", "RaaS"), ("#랜섬웨어", "랜섬웨어"),
])
def test_normalize_tag(raw, want):
    assert wiki_guard.normalize_tag(raw) == want


def test_fix_tags_and_new_page_tags(wiki):
    write(wiki, "2026-07-a", page("a", "2026-07-01", "가.", tags="[Linux kernel, 메모리 안전, Node.js, 2026]"))
    write(wiki, "2026-07-b", page("b", "2026-07-01", "나.", tags="[이미정상, RCE]", cves="\n  - CVE-2026-1"))
    stats = {}
    assert wiki_guard.fix_tags(stats) == 1
    assert "tags: [Linuxkernel, 메모리안전, Nodejs]" in read(wiki, "2026-07-a")
    assert stats["tag_values_fixed"] == 4
    assert wiki_guard.fix_tags() == 0
    item = {"id": "n", "url": "https://n/1", "title_ko": "새 사건", "tags_ko": ["공급망 공격", "C++"]}
    wiki_guard.ensure_recorded([item], {"n": {"action": "new", "kind": "incident",
                                              "topic": "new-event"}}, "2026-11-20")
    assert "tags: [공급망공격, Cpp]" in read(wiki, "2026-11-new-event")


# ------------------------------------------------------------ E8 병합과 slug 분리

def test_merge_duplicates(wiki, monkeypatch):
    monkeypatch.setattr(wiki_guard, "MERGES", {"2026-10-knx-account-lockout": "2026-07-knx-lockout"})
    write(wiki, "2026-07-knx-lockout", page(
        "knx-lockout", "2026-07-15", "정본 요약.", tags="[산업제어]", cves="[CVE-2023-4346]",
        timeline="- 2026-07-15 [NVD](https://nvd/4346) — KEV 추가",
        related="- [[knx-account-lockout]] (중복)\n- [[keep-me]]"))
    write(wiki, "2026-10-knx-account-lockout", page(
        "knx-account-lockout", "2026-07-15", "흡수 요약.", tags="[산업 자동화, 산업제어]",
        cves="[CVE-2023-4346, CVE-2023-9999]",
        timeline="- 2026-10-13 [KEV](https://nvd/4346) — 같은 URL\n- 2026-08-01 [X](https://x/1) — 새 사실"))
    write(wiki, "2026-07-keep-me", page("keep-me", "2026-07-01", "다른 페이지.",
                                        related="[[2026-10-knx-account-lockout|옛 링크]]"))
    assert wiki_guard.merge_duplicates() == 1
    assert "2026-10-knx-account-lockout" not in names(wiki)
    text = read(wiki, "2026-07-knx-lockout")
    assert "tags: [산업제어, 산업자동화]" in text
    assert "cves: [CVE-2023-4346, CVE-2023-9999]" in text
    assert "정본 요약." in text and "흡수 요약." not in text
    tl = [ln for ln in text.splitlines() if ln.startswith("- 2026")]
    assert tl == ["- 2026-07-15 [NVD](https://nvd/4346) — KEV 추가",
                  "- 2026-08-01 [X](https://x/1) — 새 사실"]
    assert "[[knx-account-lockout]]" not in text and "[[keep-me]]" in text
    wiki_guard.migrate_links()
    assert "[[2026-07-knx-lockout|옛 링크]]" in read(wiki, "2026-07-keep-me")
    assert wiki_guard.find_topic("knx-account-lockout", wiki_guard.topic_files()) == "2026-07-knx-lockout"
    assert wiki_guard.merge_duplicates() == 0


def test_rename_collisions(wiki, monkeypatch):
    monkeypatch.setattr(wiki_guard, "SLUG_RENAMES",
                        {"2026-09-velo-rce": "2026-09-velo-rce-93952"})
    write(wiki, "2026-07-velo-rce", page("velo-rce", "2026-07-27", "7월 사건."))
    write(wiki, "2026-09-velo-rce", page("velo-rce", "2026-09-22", "9월 사건."))
    write(wiki, "2026-10-ref", page("ref", "2026-10-01", "참조.", related="[[2026-09-velo-rce]]"))
    assert wiki_guard.rename_collisions() == 1
    assert "slug: velo-rce-93952" in read(wiki, "2026-09-velo-rce-93952")
    wiki_guard.migrate_links()
    assert "[[2026-09-velo-rce-93952]]" in read(wiki, "2026-10-ref")
    assert wiki_guard.find_topic("velo-rce", wiki_guard.topic_files()) == "2026-07-velo-rce"
    assert wiki_guard.rename_collisions() == 0


def test_real_merge_map_matches_qa_decision():
    assert len(wiki_guard.MERGES) == 7 and len(wiki_guard.SLUG_RENAMES) == 3
    assert wiki_guard.MERGES["2026-11-nAble-n-central-auth-bypass"] == "2026-08-n-central-auth-bypass"
    assert not any("gitlab" in k or "openai" in k for k in wiki_guard.MERGES)


# ------------------------------------------------------------ E3 원장 소급 기록

def ledger_entry(**kw):
    base = {"date": "2026-11-15", "lane": "news", "url": "https://dailysecu/1",
            "title": "", "title_ko": "", "summary_ko": "", "cves": [], "followup": False}
    base.update(kw)
    return base


def test_backfill_attaches_creates_skips_and_is_idempotent(wiki):
    write(wiki, "2026-11-voicephishing-refund-scam", page(
        "voicephishing-refund-scam", "2026-11-06",
        "공격자들이 금융보안원을 사칭하며 보이스피싱 피해금 환급 명목으로 접근하는 사기.",
        tags="[피싱, 금융사기]",
        timeline="- 2026-11-06 [뉴스](https://g/1) — 금보원 사칭 환급 사기, 피해금 환급 명목 추가 금액 요구"))
    write(wiki, "2026-11-unrelated", page("unrelated", "2026-11-10", "관련 없는 랜섬웨어 사건.",
                                          timeline="- 2026-11-10 [뉴스](https://g/2) — 랜섬웨어"))
    entries = [
        ledger_entry(url="https://dailysecu/a", date="2026-11-07",
                     title_ko="금융보안원 사칭 피해금 환급 사기 2차 피해 주의"),
        ledger_entry(url="https://thehackernews.com/2026/11/fbi-says-north-korean-hackers-stole.html",
                     title="FBI says North Korean hackers stole $400 million",
                     title_ko="FBI 북한 해커, 4억 달러 암호화폐 도난"),
        ledger_entry(url="https://x/en", title_ko="SCKit abuses ScreenConnect"),
        ledger_entry(url="https://g/1", title_ko="이미 기록됨"),
        ledger_entry(url="https://cve/1", lane="cve", title_ko="CVE 코너"),
    ]
    stats = wiki_guard.backfill_from_ledger(entries)
    assert stats == {"backfill_appended": 1, "backfill_created": 1, "backfill_skipped": 1}
    assert "— 금융보안원 사칭 피해금 환급 사기 2차 피해 주의" in read(wiki, "2026-11-voicephishing-refund-scam")
    new = read(wiki, "2026-11-fbi-says-north-korean-hackers-stole")
    assert "FBI 북한 해커, 4억 달러 암호화폐 도난" in new
    assert "North Korean hackers stole" not in new  # 영어 원제는 페이지 글로 쓰지 않는다
    assert "[thehackernews.com](https://thehackernews.com/2026/11/" in new
    assert not any("sckit" in n for n in names(wiki))
    again = wiki_guard.backfill_from_ledger(entries)
    assert (again["backfill_appended"], again["backfill_created"]) == (0, 0)


def test_backfill_does_not_attach_on_weak_overlap(wiki):
    """같은 제조사 다른 제품(RUGGEDCOM CROSSBOW ≠ APE1808)은 붙이지 않는다."""
    write(wiki, "2026-10-siemens-ruggedcom-ape1808", page(
        "siemens-ruggedcom-ape1808", "2026-10-20", "Siemens RUGGEDCOM APE1808 다수 취약점.",
        tags="[Siemens, RUGGEDCOM]",
        timeline="- 2026-10-20 [CISA](https://c/1) — Siemens RUGGEDCOM APE1808 SQL 인젝션"))
    stats = wiki_guard.backfill_from_ledger([ledger_entry(
        url="https://c/2", date="2026-10-23", title_ko="Siemens RUGGEDCOM CROSSBOW — SQL 인젝션")])
    assert stats["backfill_created"] == 1 and stats["backfill_appended"] == 0


# ------------------------------------------------------------ E1 E2 발송분 기록

def test_sent_items_recorded_without_verdict_or_with_unknown_kind(wiki):
    items = [
        {"id": "a", "url": "https://a/1", "title": "Big breach at Foo Corp",
         "title_ko": "푸 코퍼레이션 대규모 유출", "summary_ko": "**푸**에서 유출이 확인됐다.", "source": "A"},
        {"id": "b", "url": "https://b/1", "title": "Bar ransomware", "title_ko": "바 랜섬웨어 피해",
         "kind": None, "source": "B"},
        {"id": "c", "url": "https://c/1", "title_ko": "어떤 취약점 패치", "kind": "vuln"},
        {"id": "d", "url": "https://d/1", "title": "English only title", "source": "D"},
    ]
    verdicts = {"b": {"action": "new", "kind": "Breach", "topic": "bar-ransomware"}}
    stats = wiki_guard.ensure_recorded(items, verdicts, "2026-11-20", sent=True)
    assert (stats["created"], stats["skipped"]) == (2, 1)
    assert "푸 코퍼레이션 대규모 유출" in read(wiki, "2026-11-big-breach-at-foo-corp")
    assert "**푸**에서 유출이 확인됐다." in read(wiki, "2026-11-big-breach-at-foo-corp")
    assert "2026-11-bar-ransomware" in names(wiki)
    assert not any("english" in n for n in names(wiki))


@pytest.mark.parametrize("raw,want", [
    ("incident", "incident"), (" Breach ", "incident"), ("data breach", "incident"),
    ("Regulation", "policy"), ("agency", "institution"), ("vulnerability", "vuln"),
    ("misc", "other"), ("garbage", None), (["incident"], None), (None, None),
])
def test_normalize_kind(raw, want):
    assert wiki_guard.normalize_kind(raw) == want


# ------------------------------------------------------------ F3 보호 파일

def test_protected_files_are_restored(wiki):
    (wiki / "CLAUDE.md").write_text("규약", encoding="utf-8")
    (wiki / "INDEX.md").write_text("인덱스", encoding="utf-8")
    snap = wiki_guard.snapshot_protected()
    (wiki / "CLAUDE.md").write_text("사서가 덮어씀", encoding="utf-8")
    (wiki / "INDEX-archive.md").write_text("새로 만듦", encoding="utf-8")
    restored = wiki_guard.restore_protected(snap)
    assert sorted(restored) == ["CLAUDE.md", "INDEX-archive.md"]
    assert (wiki / "CLAUDE.md").read_text(encoding="utf-8") == "규약"
    assert not (wiki / "INDEX-archive.md").exists()
    assert wiki_guard.restore_protected(snap) == []


# ------------------------------------------------------------ 진입점

def test_maintenance_runs_all_steps_and_is_idempotent(wiki, monkeypatch):
    monkeypatch.setattr(wiki_guard, "MERGES", {"2026-07-dup": "2026-07-main"})
    write(wiki, "2026-07-main", page("main", "2026-07-01", "정본.",
                                     timeline="- 2026-07-01 [X](https://x/1) — 최초"))
    write(wiki, "2026-07-dup", page("dup", "2026-07-01", "중복.",
                                    timeline="- 2026-07-02 [Y](https://y/1) — 추가"))
    write(wiki, "2026-07-Upper-case", page("Upper-case", "2026-07-03", "대문자.", tags="[A B]",
                                           related="[[main]] [[ghost-hub]]"))
    first = wiki_guard.maintenance([])
    assert (first["merged"], first["lowercased"], first["tags_pages"]) == (1, 1, 1)
    assert first["links_unlinked"] == 1
    assert "[[2026-07-main]] ghost-hub" in read(wiki, "2026-07-upper-case")
    second = wiki_guard.maintenance([])
    assert not any(second[k] for k in ("merged", "slug_split", "lowercased",
                                       "tags_pages", "links_pages"))
