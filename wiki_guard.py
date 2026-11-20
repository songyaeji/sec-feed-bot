"""사서의 위키 기록을 코드가 검증·보충한다.

2026-11-20 점검 결과: 사서(Haiku)가 new·update로 답한 수보다 실제로 만들거나
고친 페이지가 매일 적었고(11-20 신규 26·갱신 9 답, 실제 생성 18·수정 8),
11-14 FBI 북한 4억 달러·11-16 SCKit은 카드로 나갔는데 위키 페이지가 아예
없었다. 모델이 규약 밖 파일(wiki/librarian_verdict.json)을 임의로 만든
흔적도 있었다. 판정과 기록이 어긋나면 위키는 사건 기록으로 쓸 수 없다.

이 모듈은 사서 실행 뒤에:
1. new·update 판정 항목마다 토픽 페이지가 있고 타임라인에 그 항목 url이
   있는지 확인하고, 없으면 코드가 최소 페이지·타임라인 줄을 직접 쓴다.
2. 확인한 페이지의 [[slug]] 링크를 Obsidian에서 열리는 [[파일명]]으로 고친다.
3. 이번 실행 중 wiki/ 아래 새로 생긴 규약 밖 파일을 지운다(실행 전부터
   있던 파일은 건드리지 않는다).

위키 페이지는 사고·법제도·기관 발표만 만든다(kind incident·policy·
institution, 사용자 결정 2026-11-20). kind가 없으면(구 출력) 판정을 믿는다.
"""
import glob
import hashlib
import os
import re
import sys

import dedup as dedup_lib
from wiki_index import TOPICS_DIR, WIKI_DIR

WIKI_KINDS = {"incident", "policy", "institution"}
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,80}$")
_LINK_RE = re.compile(r"\[\[([^\]|#]+)(\|[^\]]*)?\]\]")
_ALLOWED_ROOT = {"INDEX.md", "INDEX-archive.md", "CLAUDE.md"}


# ------------------------------------------------------------ 파일 목록

def snapshot() -> set[str]:
    """wiki/ 아래 파일 상대경로 집합 — 사서 실행 전에 찍어 둔다."""
    out = set()
    for root, _, files in os.walk(WIKI_DIR):
        for name in files:
            out.add(os.path.relpath(os.path.join(root, name), WIKI_DIR).replace("\\", "/"))
    return out


def _allowed(rel: str) -> bool:
    if rel in _ALLOWED_ROOT or rel == "topics/.gitkeep":
        return True
    return rel.startswith("topics/") and rel.endswith(".md") and rel.count("/") == 1


def remove_stray(before: set[str]) -> list[str]:
    """이번 실행에서 새로 생긴 규약 밖 파일을 지운다. 지운 목록 반환."""
    removed = []
    for rel in sorted(snapshot() - before):
        if _allowed(rel):
            continue
        try:
            os.remove(os.path.join(WIKI_DIR, rel))
            removed.append(rel)
        except OSError:
            continue
    if removed:
        print(f"[wiki] 규약 밖 파일 삭제: {removed}", file=sys.stderr)
    return removed


# ------------------------------------------------------------ 토픽 파일

def topic_files() -> dict[str, str]:
    """파일명(확장자 없음) → 경로."""
    return {os.path.basename(p)[:-3]: p
            for p in glob.glob(os.path.join(TOPICS_DIR, "*.md"))}


def find_topic(slug: str, files: dict[str, str]) -> str | None:
    """slug로 토픽 파일 찾기 — 파일명이 slug이거나 'YYYY-MM-slug'인 것. 여럿이면 최신."""
    hits = sorted(n for n in files
                  if n == slug or re.fullmatch(rf"\d{{4}}-\d{{2}}-{re.escape(slug)}", n))
    return hits[-1] if hits else None


def _fallback_slug(item: dict) -> str:
    words = re.findall(r"[a-z0-9]+", (item.get("title") or "").lower())
    words = [w for w in words if len(w) > 1][:6]
    if len(words) >= 2:
        return "-".join(words)[:60].strip("-")
    digest = hashlib.sha1((item.get("url") or item.get("id") or "").encode()).hexdigest()[:8]
    return f"event-{digest}"


def _timeline_line(item: dict, day: str) -> str:
    source = (item.get("source") or "출처").replace("[", "").replace("]", "")
    fact = " ".join((item.get("title_ko") or item.get("title") or "").replace("**", "").split())
    return f"- {day} [{source}]({item.get('url', '')}) — {fact}"


def _new_page(slug: str, item: dict, day: str) -> str:
    text = f"{item.get('title', '')} {item.get('summary', '')}"
    cves = sorted(dedup_lib.extract_cves(text))
    tags = [t for t in (item.get("tags_ko") or []) if isinstance(t, str)][:4]
    summary = " ".join((item.get("summary_ko") or item.get("title_ko")
                        or item.get("title") or "").split())
    return (
        "---\n"
        f"slug: {slug}\n"
        f"first_seen: {day}\n"
        f"tags: [{', '.join(tags)}]\n"
        f"cves: [{', '.join(cves)}]\n"
        "---\n\n"
        f"{summary}\n\n"
        "## 타임라인\n\n"
        f"{_timeline_line(item, day)}\n\n"
        "## 관련\n"
    )


def _insert_timeline(text: str, line: str) -> str:
    """'## 타임라인' 구역에 날짜 순서를 지켜 한 줄 끼운다. 구역이 없으면 만든다."""
    if "## 타임라인" not in text:
        anchor = text.find("## 관련")
        block = f"## 타임라인\n\n{line}\n\n"
        return (text[:anchor] + block + text[anchor:]) if anchor != -1 else (
            text.rstrip("\n") + "\n\n" + block)
    head, rest = text.split("## 타임라인", 1)
    nxt = re.search(r"\n## ", rest)
    section = rest[:nxt.start()] if nxt else rest
    tail = rest[nxt.start():] if nxt else ""  # "\n## 관련..." 으로 시작
    lines = section.strip("\n").split("\n") if section.strip() else []
    entries = [ln for ln in lines if ln.startswith("- ")]
    others = [ln for ln in lines if not ln.startswith("- ")]
    entries.append(line)
    # 안정 정렬 — 같은 날짜 줄은 기존 순서 뒤에 붙는다
    entries.sort(key=lambda ln: ln[2:12])
    body = "\n".join([*others, *entries]).strip("\n")
    return f"{head}## 타임라인\n\n{body}\n{tail}"


def fix_links(text: str, files: dict[str, str]) -> str:
    """[[slug]] → [[YYYY-MM-slug]] (Obsidian은 파일명으로만 링크를 연다)."""
    def repl(m):
        target = m.group(1).strip()
        if target in files:
            return m.group(0)
        name = find_topic(target, files)
        return f"[[{name}{m.group(2) or ''}]]" if name else m.group(0)
    return _LINK_RE.sub(repl, text)


# ------------------------------------------------------------ 검증

def ensure_recorded(items: list[dict], verdicts: dict, day: str) -> dict:
    """new·update 판정 항목의 위키 기록을 확인·보충. 집계 dict 반환."""
    files = topic_files()
    stats = {"checked": 0, "created": 0, "appended": 0, "links": 0}
    touched: set[str] = set()
    for item in items:
        v = verdicts.get(item.get("id"))
        if not isinstance(v, dict) or v.get("action") not in ("new", "update"):
            continue
        kind = v.get("kind")
        if not isinstance(kind, str):
            kind = None  # 리스트 등 이상값은 미분류 취급 — set 조회 TypeError 방지
        if kind is not None and kind not in WIKI_KINDS:
            continue
        stats["checked"] += 1
        slug = v.get("topic") if isinstance(v.get("topic"), str) else ""
        slug = slug.strip().lower()
        if not _SLUG_RE.match(slug):
            slug = _fallback_slug(item)
            v["topic"] = slug
        name = find_topic(slug, files)
        if name is None:
            name = f"{day[:7]}-{slug}"
            path = os.path.join(TOPICS_DIR, f"{name}.md")
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(_new_page(slug, item, day))
            files[name] = path
            stats["created"] += 1
            print(f"[wiki] 사서가 안 쓴 페이지 보충 생성: {name}", file=sys.stderr)
            touched.add(name)
            continue
        path = files[name]
        with open(path, encoding="utf-8") as f:
            text = f.read()
        url = item.get("url") or ""
        if url and url not in text:
            text = _insert_timeline(text, _timeline_line(item, day))
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            stats["appended"] += 1
            print(f"[wiki] 사서가 안 쓴 타임라인 줄 보충: {name}", file=sys.stderr)
        touched.add(name)

    for name in touched:
        path = files[name]
        with open(path, encoding="utf-8") as f:
            text = f.read()
        fixed = fix_links(text, files)
        if fixed != text:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(fixed)
            stats["links"] += 1
    print(f"[wiki] 기록 검증: 확인 {stats['checked']}건, 페이지 보충 "
          f"{stats['created']}건, 타임라인 보충 {stats['appended']}건, "
          f"링크 정리 {stats['links']}개 페이지", file=sys.stderr)
    return stats


def migrate_links() -> int:
    """기존 전 페이지의 [[slug]] 링크를 [[파일명]]으로 1회 변환. 바뀐 페이지 수."""
    files = topic_files()
    changed = 0
    for name, path in files.items():
        with open(path, encoding="utf-8") as f:
            text = f.read()
        fixed = fix_links(text, files)
        if fixed != text:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(fixed)
            changed += 1
    return changed


if __name__ == "__main__":
    # 1회성: python wiki_guard.py migrate-links
    if sys.argv[1:] == ["migrate-links"]:
        print(f"링크 변환 페이지 {migrate_links()}개")
    else:
        print("usage: python wiki_guard.py migrate-links", file=sys.stderr)
        sys.exit(2)
