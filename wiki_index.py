"""위키 INDEX.md 정리(아카이브 이동)."""
import os
import re
import sys
from datetime import datetime, timedelta, timezone

from common import BASE_DIR

# 위키 INDEX 정리 — 사서가 배치마다 INDEX 전체를 읽으므로 무한 성장은
# 배치 시간 증가 → 300s 타임아웃 → 뉴스 무판정 유실로 되돌아온다
# (2026-07-12 실측: 위키 성장으로 20건 배치가 타임아웃, 12건으로 축소).
# 오래된 토픽 줄은 목록만 아카이브로 옮긴다 — 토픽 페이지는 그대로 남고
# 사서도 Grep(wiki/**)으로 여전히 찾을 수 있다.
WIKI_INDEX_PATH = os.path.join(BASE_DIR, "wiki", "INDEX.md")
WIKI_INDEX_ARCHIVE_PATH = os.path.join(BASE_DIR, "wiki", "INDEX-archive.md")
_INDEX_DATE_RE = re.compile(r"\(최종갱신일:\s*(\d{4}-\d{2}-\d{2})\)\s*$")


def _prune_wiki_index(max_age_days: int) -> None:
    try:
        with open(WIKI_INDEX_PATH, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return
    cutoff = (
        datetime.now(timezone(timedelta(hours=9))) - timedelta(days=max_age_days)
    ).strftime("%Y-%m-%d")
    keep: list[str] = []
    stale: list[str] = []
    for line in lines:
        m = _INDEX_DATE_RE.search(line)
        if m and line.lstrip().startswith("-") and m.group(1) < cutoff:
            stale.append(line)
        else:
            keep.append(line)
    if not stale:
        return
    try:
        header_needed = not os.path.exists(WIKI_INDEX_ARCHIVE_PATH)
        with open(WIKI_INDEX_ARCHIVE_PATH, "a", encoding="utf-8") as f:
            if header_needed:
                f.write("# 보안동향 위키 인덱스 아카이브\n\n")
                f.write("최종갱신일이 오래돼 INDEX.md에서 옮겨진 토픽 목록"
                        "(자동 이동 — main._prune_wiki_index).\n\n")
            f.write("\n".join(stale) + "\n")
        with open(WIKI_INDEX_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(keep) + "\n")
        print(
            f"[main] 위키 INDEX 정리: {len(stale)}건 아카이브(기준 {max_age_days}일)",
            file=sys.stderr,
        )
    except OSError as exc:
        print(f"[main] 위키 INDEX 정리 실패(무시): {exc}", file=sys.stderr)
