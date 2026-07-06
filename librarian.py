"""2nd-layer LLM wiki librarian (digest mode only).

Calls a headless Claude Code subprocess that reads wiki/CLAUDE.md, updates
wiki/topics/*.md and wiki/INDEX.md, and returns a verdict per item so
main.py can drop items that are already covered in the wiki
(action == "skip_duplicate") from the digest.

This is a nice-to-have layered on top of dedup.py's heuristic filter, never
a hard dependency: any failure (subprocess error, timeout, unparsable
output, missing token) returns None so main.py can fail-open and send
everything -- a wiki-sync problem must never suppress a real alert.
"""
import json
import os
import subprocess
import sys

import dedup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")
LIBRARIAN_INPUT_PATH = os.path.join(STATE_DIR, "librarian_input.json")
LIBRARIAN_PROMPT_PATH = os.path.join(BASE_DIR, "librarian_prompt.md")

TIMEOUT_SECONDS = 300
MODEL = "claude-haiku-4-5-20251001"


def _item_to_input(item: dict) -> dict:
    text = f"{item.get('title', '')} {item.get('summary', '')}"
    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "summary": item.get("summary"),
        "url": item.get("url"),
        "source": item.get("source"),
        "tags": item.get("tags", []),
        "cves": sorted(dedup.extract_cves(text)),
    }


def _write_input(items: list[dict]) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    payload = [_item_to_input(item) for item in items]
    with open(LIBRARIAN_INPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _extract_json_object(text: str):
    # the model is instructed to answer with JSON only, but be lenient in
    # case it wraps the object in a code fence or adds stray whitespace
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object found in librarian output")
    return json.loads(text[start:end + 1])


def run_librarian(items: list[dict]) -> dict | None:
    """Returns {"briefing": str | None, "verdicts": {item_id: {"action": ...,
    "topic": ...}}} on success, or None on any failure (fail-open -- caller
    must send everything when this returns None). "briefing" defaults to
    None if the model's output omits it."""
    if not items:
        return None

    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        print("[librarian] CLAUDE_CODE_OAUTH_TOKEN 미설정 — 위키 사서 스킵", file=sys.stderr)
        return None

    try:
        _write_input(items)
        with open(LIBRARIAN_PROMPT_PATH, "r", encoding="utf-8") as f:
            prompt = f.read()
    except OSError as exc:
        print(f"[librarian] 입력 준비 실패: {exc}", file=sys.stderr)
        return None

    try:
        proc = subprocess.run(
            [
                # --bare는 credentials 파일까지 스킵해 CI에서 "Not logged in"이 됨 (2.1.201 실측)
                "claude", "-p", prompt,
                "--model", MODEL,
                "--allowedTools", "Read,Write,Edit,Glob,Grep",
                "--permission-mode", "acceptEdits",
                "--output-format", "json",
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[librarian] 실행 실패: {exc}", file=sys.stderr)
        return None

    if proc.returncode != 0:
        # 오류 본문이 stderr가 아니라 stdout(JSON)에 실리는 경우가 있어 둘 다 남긴다
        print(
            f"[librarian] 비정상 종료 (code={proc.returncode}) "
            f"stderr: {proc.stderr[:300]} | stdout: {proc.stdout[:500]}",
            file=sys.stderr,
        )
        return None

    try:
        outer = json.loads(proc.stdout)
        result_text = outer["result"]
        verdicts = _extract_json_object(result_text)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"[librarian] 응답 파싱 실패: {exc}", file=sys.stderr)
        return None

    if "verdicts" not in verdicts:
        print("[librarian] 응답에 'verdicts' 키 없음", file=sys.stderr)
        return None

    # briefing is a nice-to-have on top of verdicts -- if the model omits
    # it, default to None rather than failing the whole (already-successful)
    # librarian run
    verdicts.setdefault("briefing", None)

    return verdicts
