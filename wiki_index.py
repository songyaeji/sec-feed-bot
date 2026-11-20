"""위키 INDEX 재생성 — 토픽 페이지가 정본, INDEX는 코드가 만든다.

2026-11-20 교체. 구 방식은 사서(LLM)가 INDEX에 줄을 직접 쓰고 코드는 오래된
줄만 아카이브로 옮겼다. 점검 결과 INDEX와 아카이브에 같은 페이지 중복 줄
34개, 어느 INDEX에도 없는 페이지 36개, 없는 파일을 가리키는 줄 2개가
쌓였다. 이제 사서는 INDEX를 읽기만 하고, 코드가 wiki/topics/*.md 전체에서
INDEX.md(최근 갱신)와 INDEX-archive.md(그보다 오래된 것)를 다시 만든다.

한줄요약은 기존 INDEX·아카이브 줄에 있던 문구를 그대로 쓰고(불필요한
문구 변경 방지), 줄이 없던 페이지만 페이지 본문 첫 문장으로 만든다.
사서가 배치마다 INDEX 전체를 읽으므로 최근 줄만 남기는 다이어트 목적은
그대로다(2026-07-12 실측: 위키 성장으로 배치 타임아웃).
"""
import glob
import os
import re
import sys
from datetime import datetime, timedelta, timezone

from common import BASE_DIR

WIKI_DIR = os.path.join(BASE_DIR, "wiki")
TOPICS_DIR = os.path.join(WIKI_DIR, "topics")
WIKI_INDEX_PATH = os.path.join(WIKI_DIR, "INDEX.md")
WIKI_INDEX_ARCHIVE_PATH = os.path.join(WIKI_DIR, "INDEX-archive.md")

_INDEX_LINE_RE = re.compile(
    r"^- \[[^\]]*\]\(topics/([^)]+)\.md\)\s*(.*?)\s*\(최종갱신일:\s*(\d{4}-\d{2}-\d{2})\)\s*$")
_FM_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)
_TIMELINE_DATE_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) ", re.M)
_SENT_END_RE = re.compile(r"(?<=[.!?다])\s")

INDEX_HEADER = (
    "# 보안동향 위키 인덱스\n\n"
    "형식: `- [slug](topics/파일명.md) 한줄요약 (최종갱신일: YYYY-MM-DD)`\n"
    "자동 생성(wiki_index.rebuild_index) — 손으로 고치지 않는다. 토픽 페이지가 정본이다.\n\n"
)
ARCHIVE_HEADER = (
    "# 보안동향 위키 인덱스 아카이브\n\n"
    "최종갱신일이 오래돼 INDEX.md에서 빠진 토픽 목록"
    "(자동 생성 — wiki_index.rebuild_index).\n\n"
)
SUMMARY_MAX = 90


def frontmatter(text: str) -> dict:
    m = _FM_RE.match(text)
    out: dict = {}
    if not m:
        return out
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"\'')
    return out


def body_summary(text: str) -> str:
    """페이지 본문 첫 문단의 첫 문장 — 기존 INDEX 줄이 없는 페이지용."""
    body = _FM_RE.sub("", text, count=1)
    for para in body.split("\n\n"):
        para = " ".join(para.replace("**", "").split())
        if para and not para.startswith("#") and not para.startswith("- "):
            first = _SENT_END_RE.split(para, maxsplit=1)[0].rstrip(".")
            return first[:SUMMARY_MAX]
    return ""


def last_updated(text: str, fm: dict, name: str) -> str:
    dates = _TIMELINE_DATE_RE.findall(text)
    if dates:
        return max(dates)
    fs = fm.get("first_seen", "")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", fs):
        return fs
    return f"{name[:7]}-01" if re.match(r"\d{4}-\d{2}", name) else "1970-01-01"


def _existing_summaries() -> dict[str, str]:
    """페이지별 기존 한줄요약. 중복 줄이면 최종갱신일이 가장 늦은 줄의 문구."""
    best: dict[str, tuple[str, str]] = {}
    for path in (WIKI_INDEX_ARCHIVE_PATH, WIKI_INDEX_PATH):  # 같은 날짜면 INDEX 쪽 우선
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    m = _INDEX_LINE_RE.match(line.rstrip("\n"))
                    if not m or not m.group(2):
                        continue
                    name, summary, date = m.groups()
                    if name not in best or date >= best[name][0]:
                        best[name] = (date, summary)
        except OSError:
            continue
    return {name: summary for name, (_, summary) in best.items()}


def rebuild_index(max_age_days: int, now: datetime | None = None) -> tuple[int, int]:
    """INDEX.md·INDEX-archive.md를 토픽 페이지에서 다시 만든다. (최근, 아카이브) 줄 수."""
    now = now or datetime.now(timezone(timedelta(hours=9)))
    cutoff = (now - timedelta(days=max_age_days)).strftime("%Y-%m-%d")
    summaries = _existing_summaries()
    rows = []
    for path in glob.glob(os.path.join(TOPICS_DIR, "*.md")):
        name = os.path.basename(path)[:-3]
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        fm = frontmatter(text)
        slug = fm.get("slug") or re.sub(r"^\d{4}-\d{2}-", "", name)
        summary = summaries.get(name) or body_summary(text) or slug
        date = last_updated(text, fm, name)
        rows.append((date, name, f"- [{slug}](topics/{name}.md) {summary} (최종갱신일: {date})"))
    rows.sort(key=lambda r: (r[0], r[1]), reverse=True)
    recent = [line for d, _, line in rows if d >= cutoff]
    old = [line for d, _, line in rows if d < cutoff]
    try:
        with open(WIKI_INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(INDEX_HEADER + "\n".join(recent) + "\n")
        with open(WIKI_INDEX_ARCHIVE_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(ARCHIVE_HEADER + "\n".join(old) + "\n")
    except OSError as exc:
        print(f"[wiki] INDEX 재생성 실패(무시): {exc}", file=sys.stderr)
        return 0, 0
    print(f"[wiki] INDEX 재생성: 최근 {len(recent)}줄, 아카이브 {len(old)}줄 "
          f"(기준 {max_age_days}일)", file=sys.stderr)
    return len(recent), len(old)
