"""2nd-layer LLM wiki librarian (digest mode only).

Calls a headless Claude Code subprocess that reads wiki/CLAUDE.md, updates
wiki/topics/*.md and wiki/INDEX.md, and returns a verdict per item so
main.py can drop items that are already covered in the wiki
(action == "skip_duplicate") from the digest.

This is a nice-to-have layered on top of dedup.py's heuristic filter, never
a hard dependency: total failure (subprocess error, timeout, unparsable
output, missing token) returns None so main.py can fail-open with its own
heuristic top-N -- a wiki-sync problem must never suppress a real alert.
"""
import json
import os
import re
import subprocess
import sys

import dedup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")
LIBRARIAN_INPUT_PATH = os.path.join(STATE_DIR, "librarian_input.json")
LIBRARIAN_PROMPT_PATH = os.path.join(BASE_DIR, "librarian_prompt.md")

TIMEOUT_SECONDS = 300  # 청크당
MODEL = "claude-haiku-4-5-20251001"
# 276건을 한 번에 넣으면 모델이 최종 JSON을 못 뱉고 무너진다(실측) —
# 한 subprocess가 감당할 수 있는 크기로 잘라 순차 처리한다.
# 25건은 300초 타임아웃을 종종 넘겼다(2026-07-07 하루 두 번, 청크째 유실) → 20건
BATCH_SIZE = 20


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


_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _style_ok(text: str) -> bool:
    """summary_ko 문체 게이트 — 모든 문장이 완결형 종결어미('~다')로
    끝나는지. 명사형(개조식) 종결("~플랫폼 분석.")은 카드 본문 품질
    기준 미달(사용자 피드백 v20 — 프롬프트 규칙만으로는 안 지켜짐)."""
    plain = text.replace("**", "").strip()
    if not plain:
        return True
    for sent in _SENT_SPLIT_RE.split(plain):
        sent = sent.strip().rstrip('.!?"\')』」]')
        if sent and not sent.endswith("다"):
            return False
    return True


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


def _run_chunk(chunk: list[dict], prompt: str) -> dict | None:
    """청크 하나를 subprocess로 처리해 해당 청크의 verdicts dict를 돌려준다.
    어떤 실패든 None — 호출자(run_librarian)가 그 청크만 스킵하고 계속한다."""
    try:
        _write_input(chunk)
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
        parsed = _extract_json_object(result_text)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"[librarian] 응답 파싱 실패: {exc}", file=sys.stderr)
        return None

    if "verdicts" not in parsed:
        print("[librarian] 응답에 'verdicts' 키 없음", file=sys.stderr)
        return None

    return parsed["verdicts"]


def _fix_styles(verdicts: dict, model: str, timeout: int) -> None:
    """개조식 summary_ko를 완결형으로 고치는 교정 재호출 1회.
    실패해도 원문 유지(fail-open) — verdicts를 제자리에서 고친다."""
    bad = {
        vid: v["summary_ko"]
        for vid, v in verdicts.items()
        if v.get("summary_ko") and not _style_ok(v["summary_ko"])
    }
    if not bad:
        return

    prompt = (
        "아래 보안 뉴스 요약들은 명사형(개조식)으로 끝나는 문장이 있다. "
        "각 요약의 뜻·키워드(**별표 마커** 포함)를 그대로 유지하면서, "
        "모든 문장이 '~했다/~한다/~이다' 완결형 종결어미로 끝나게만 고쳐 써라. "
        'JSON 하나만 출력: {"<id>": "<고친 요약>", ...}\n\n'
        + json.dumps(bad, ensure_ascii=False)
    )

    fixed = None
    try:
        proc = subprocess.run(
            [
                "claude", "-p", prompt,
                "--model", model,
                "--output-format", "json",
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode == 0:
            outer = json.loads(proc.stdout)
            fixed = _extract_json_object(outer["result"])
    except (subprocess.TimeoutExpired, OSError,
            json.JSONDecodeError, KeyError, TypeError, ValueError):
        fixed = None

    if not isinstance(fixed, dict):
        print(f"[librarian] 문체 교정 실패 — 원문 발송 {len(bad)}건", file=sys.stderr)
        return

    passed = 0
    for vid in bad:
        new_summary = fixed.get(vid)
        if isinstance(new_summary, str) and new_summary.strip() and _style_ok(new_summary):
            verdicts[vid]["summary_ko"] = new_summary
            passed += 1
    print(f"[librarian] 개조식 요약 {len(bad)}건 교정 → {passed}건 통과", file=sys.stderr)


def run_librarian(items: list[dict]) -> dict | None:
    """Returns {"verdicts": {item_id: {"action": ..., "topic": ...,
    "importance": ...}}} on success, or None on total failure (fail-open --
    caller must apply its own cap when this returns None).

    아이템을 BATCH_SIZE 청크로 잘라 순차 처리한다 — 위키 편집이 누적되므로
    병렬 금지. 일부 청크가 실패해도 나머지 verdicts로 부분 성공을 돌려주고,
    모든 청크가 실패했을 때만 None(기존 fail-open 계약 유지). 총평/키워드는
    별도 summarize() 호출로 분리됐다."""
    if not items:
        return None

    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        print("[librarian] CLAUDE_CODE_OAUTH_TOKEN 미설정 — 위키 사서 스킵", file=sys.stderr)
        return None

    try:
        with open(LIBRARIAN_PROMPT_PATH, "r", encoding="utf-8") as f:
            prompt = f.read()
    except OSError as exc:
        print(f"[librarian] 프롬프트 읽기 실패: {exc}", file=sys.stderr)
        return None

    chunks = [items[i:i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]
    merged_verdicts: dict = {}
    lost = 0
    for i, chunk in enumerate(chunks, start=1):
        print(f"[librarian] 배치 {i}/{len(chunks)}: {len(chunk)}건", file=sys.stderr)
        chunk_verdicts = _run_chunk(chunk, prompt)
        if chunk_verdicts is None:
            # 실패 배치는 반으로 쪼개 각 1회 재시도 — 타임아웃 원인 대부분이
            # 배치 크기라서 절반이면 제한 내 완료 확률이 크게 오른다.
            # 여기서도 실패한 반쪽만 유실(기존 부분 성공 계약 유지)
            print(f"[librarian] 배치 {i}/{len(chunks)} 실패 — 반으로 쪼개 재시도", file=sys.stderr)
            mid = (len(chunk) + 1) // 2
            for j, half in enumerate((chunk[:mid], chunk[mid:]), start=1):
                if not half:
                    continue
                half_verdicts = _run_chunk(half, prompt)
                if half_verdicts is None:
                    lost += len(half)
                    print(
                        f"[librarian] 배치 {i} 재시도 {j}/2 실패 — {len(half)}건 스킵",
                        file=sys.stderr,
                    )
                    continue
                merged_verdicts.update(half_verdicts)
            continue
        merged_verdicts.update(chunk_verdicts)

    if not merged_verdicts:
        # 부분 성공조차 없으면 기존 계약대로 None — main.py가 fail-open
        return None
    if lost:
        print(f"[librarian] 재시도까지 실패 {lost}건 유실 — 부분 성공으로 계속", file=sys.stderr)

    _fix_styles(merged_verdicts, MODEL, 120)
    return {"verdicts": merged_verdicts}


def summarize(items: list[dict]) -> dict | None:
    """카드에 실릴 최종 아이템(≤12건)으로 표지용 총평·키워드를 만든다.
    반환: {"briefing": str, "keywords": [str, ...]} — 어떤 실패든 None
    (fail-open: 표지는 briefing 없이도, 키워드는 태그 폴백으로 나간다).

    위키 편집이 필요 없는 순수 텍스트 요약이라 파일 입출력·도구 없이
    프롬프트에 항목을 직접 넣는다."""
    if not items:
        return None

    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        print("[librarian] CLAUDE_CODE_OAUTH_TOKEN 미설정 — 총평 스킵", file=sys.stderr)
        return None

    lines = []
    for i, item in enumerate(items, start=1):
        title = (item.get("title_ko") or item.get("title") or "")[:200]
        summary = (item.get("summary_ko") or item.get("summary") or "")[:200]
        lines.append(f"{i}. {title} — {summary}")

    prompt = (
        "너는 보안 카드뉴스 편집장이다. 아래 오늘의 항목들을 관통하는 "
        "한국어 총평 2~3문장(briefing)과 핵심 키워드 3~5개(keywords)를 "
        "JSON 하나로만 출력하라.\n\n"
        "briefing 규칙: 모든 문장은 '~했다/~한다/~이다' 완결형 종결어미로 "
        "끝낸다 — 명사형(개조식) 종결 금지.\n\n"
        "키워드 규칙: 한국어, 공백 없이 (표지에 #키워드 해시태그로 실린다. "
        "예: \"AI에이전트\", \"랜섬웨어\", \"공급망공격\"). 보안 통용 약어"
        "(APT·LLM)만 영문 허용, 그 외는 한국어로 쓴다. AI 관련 키워드가 "
        "있으면 우선 포함한다.\n\n"
        "출력 형식 (설명 텍스트·코드블록 없이 JSON 그 자체):\n"
        '{"briefing": "...", "keywords": ["...", ...]}\n\n'
        "오늘의 항목:\n" + "\n".join(lines)
    )

    try:
        proc = subprocess.run(
            [
                # 파일 편집이 필요 없으므로 --allowedTools 없이(도구 불필요)
                "claude", "-p", prompt,
                "--model", MODEL,
                "--output-format", "json",
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[librarian] 총평 실행 실패: {exc}", file=sys.stderr)
        return None

    if proc.returncode != 0:
        print(
            f"[librarian] 총평 비정상 종료 (code={proc.returncode}) "
            f"stderr: {proc.stderr[:300]} | stdout: {proc.stdout[:500]}",
            file=sys.stderr,
        )
        return None

    try:
        outer = json.loads(proc.stdout)
        return _extract_json_object(outer["result"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"[librarian] 총평 파싱 실패: {exc}", file=sys.stderr)
        return None
