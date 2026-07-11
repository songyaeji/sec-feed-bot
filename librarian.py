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
import signal
import subprocess
import sys
import time

import dedup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")
LIBRARIAN_INPUT_PATH = os.path.join(STATE_DIR, "librarian_input.json")
LIBRARIAN_PROMPT_PATH = os.path.join(BASE_DIR, "librarian_prompt.md")

TIMEOUT_SECONDS = 300  # 청크당
# 전역 시간예산 — 배치가 아무리 많아도(255건=13배치) 이 벽에서 멈추고
# 부분 성공(fail-open 계약)으로 넘어간다. 없으면 배치×timeout이 GitHub
# Actions 6h 상한까지 쌓여 concurrency 그룹을 동결시킨다(2026-07-10 실측:
# digest run이 1h23m hang). workflow의 timeout-minutes와 이중 방어.
DEADLINE_SECONDS = 900  # 15분 — 최악(마지막 배치 직전 통과 + 청크 300s)
# ≈ 20분이라 workflow step timeout 25분 안에 확실히 끝난다
MODEL = "claude-haiku-4-5-20251001"


def _run_claude_json(extra_args: list[str], prompt: str, timeout: int):
    """`claude -p ... --output-format json` 을 새 프로세스그룹으로 띄워
    timeout 시 그룹째 SIGKILL 한다. subprocess.run(timeout=)은 직속 자식만
    죽여서, claude CLI가 남긴 node 손자프로세스가 stdout 파이프를 붙들면
    communicate()가 timeout을 넘겨 무한 블록한다(2026-07-10 digest 1h23m
    hang의 실제 원인). start_new_session으로 프로세스그룹을 분리하고
    killpg로 손자까지 회수해 timeout을 실효화한다.
    반환: CompletedProcess, 또는 timeout/OSError 시 None."""
    try:
        proc = subprocess.Popen(
            ["claude", "-p", prompt, *extra_args, "--output-format", "json"],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
    except OSError as exc:
        print(f"[librarian] claude 기동 실패: {exc}", file=sys.stderr)
        return None

    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        proc.wait()
        print(f"[librarian] claude 타임아웃 {timeout}s — 프로세스그룹 kill", file=sys.stderr)
        return None
    except OSError as exc:
        print(f"[librarian] claude 통신 실패: {exc}", file=sys.stderr)
        return None

    return subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)


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
        "published": item.get("published"),
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
    """summary_ko/why_ko 문체 게이트 — 모든 문장이 완결형 종결어미('~다')로
    끝나고 텍스트가 마침표('.')로 닫히는지. 명사형(개조식) 종결
    ("~플랫폼 분석.")은 카드 본문 품질 기준 미달(사용자 피드백 v20 —
    프롬프트 규칙만으로는 안 지켜짐). 마침표 종결까지 강제하는 건
    "했다"처럼 완결형이지만 마침표가 빠져 문체가 들쭉날쭉한 것을 막기
    위함이다(사용자 피드백 — 종결 부호 통일). term_ko("용어 — 정의"
    명사구)는 검사 대상이 아니다."""
    plain = text.replace("**", "").strip()
    if not plain:
        return True
    # 전체 텍스트는 마침표로 닫혀야 한다 — 마지막 문장의 종결 부호 누락 차단
    if not plain.endswith("."):
        return False
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

    proc = _run_claude_json(
        [
            # --bare는 credentials 파일까지 스킵해 CI에서 "Not logged in"이 됨 (2.1.201 실측)
            "--model", MODEL,
            # 피드 본문은 신뢰할 수 없는 입력 — 경로 무제한 Read/Write는
            # 프롬프트 인젝션 시 자격증명 파일을 읽어 wiki 페이지(커밋되어
            # 공개 repo로 push됨)에 쓰는 유출 경로가 된다. 도구를 위키와
            # 입력 파일로 스코프하고, 경로 무관 자동승인이라 allowlist를
            # 무력화하는 acceptEdits 모드는 제거(비대화형 -p에서 allowlist
            # 밖 도구 호출은 자동 거부된다)
            "--allowedTools",
            "Read(wiki/**),Read(state/librarian_input.json),"
            "Write(wiki/**),Edit(wiki/**),Glob(wiki/**),Grep(wiki/**)",
        ],
        prompt,
        TIMEOUT_SECONDS,
    )
    if proc is None:
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
    """개조식 summary_ko/why_ko를 완결형으로 고치는 교정 재호출 1회.
    실패해도 원문 유지(fail-open) — verdicts를 제자리에서 고친다."""
    bad: dict = {}
    for vid, v in verdicts.items():
        fields = {
            key: v[key]
            for key in ("summary_ko", "why_ko")
            if v.get(key) and not _style_ok(v[key])
        }
        if fields:
            bad[vid] = fields
    if not bad:
        return

    prompt = (
        "아래 보안 뉴스 텍스트들은 명사형(개조식)으로 끝나거나 마침표 없이 "
        "끝나는 문장이 있다. "
        "각 텍스트의 뜻·키워드(**별표 마커** 포함)를 그대로 유지하면서, "
        "모든 문장이 '~했다/~한다/~이다' 완결형 종결어미로 끝나고 각 문장을 "
        "마침표('.')로 닫게만 고쳐 써라. "
        "입력과 같은 구조(id·필드명 유지)로 JSON 하나만 출력: "
        '{"<id>": {"summary_ko": "<고친 요약>", "why_ko": "<고친 문장>"}, ...} '
        "— 각 id에는 입력에 있던 필드만 넣는다.\n\n"
        + json.dumps(bad, ensure_ascii=False)
    )

    fixed = None
    proc = _run_claude_json(["--model", model], prompt, timeout)
    if proc is not None and proc.returncode == 0:
        try:
            outer = json.loads(proc.stdout)
            fixed = _extract_json_object(outer["result"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            fixed = None

    total = sum(len(fields) for fields in bad.values())
    if not isinstance(fixed, dict):
        print(f"[librarian] 문체 교정 실패 — 원문 발송 {total}건", file=sys.stderr)
        return

    passed = 0
    for vid, fields in bad.items():
        fixed_fields = fixed.get(vid)
        if not isinstance(fixed_fields, dict):
            continue
        for key in fields:
            new_text = fixed_fields.get(key)
            if isinstance(new_text, str) and new_text.strip() and _style_ok(new_text):
                verdicts[vid][key] = new_text
                passed += 1
    print(f"[librarian] 개조식 텍스트 {total}건 교정 → {passed}건 통과", file=sys.stderr)


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
    start = time.monotonic()
    for i, chunk in enumerate(chunks, start=1):
        # 전역 시간예산 초과 시 남은 배치는 처리하지 않고 부분 성공으로 종료.
        # 각 subprocess가 killpg로 실제 timeout을 지키므로 이 검사가 배치마다
        # 반드시 도달한다(예산 없으면 13배치×재시도가 6h까지 누적).
        if time.monotonic() - start > DEADLINE_SECONDS:
            remaining = sum(len(c) for c in chunks[i - 1:])
            lost += remaining
            print(
                f"[librarian] 전역 예산 {DEADLINE_SECONDS}s 초과 — "
                f"남은 {remaining}건 스킵, 부분 성공으로 종료",
                file=sys.stderr,
            )
            break
        print(f"[librarian] 배치 {i}/{len(chunks)}: {len(chunk)}건", file=sys.stderr)
        chunk_verdicts = _run_chunk(chunk, prompt)
        if chunk_verdicts is None:
            # 실패 배치는 반으로 쪼개 각 1회 재시도 — 타임아웃 원인 대부분이
            # 배치 크기라서 절반이면 제한 내 완료 확률이 크게 오른다.
            # 여기서도 실패한 반쪽만 유실(기존 부분 성공 계약 유지)
            # 재시도도 예산을 본다 — 예산 초과 후의 반쪼개 2회(최대 600s)가
            # step timeout을 뚫는 걸 막는다. 초과면 이 배치는 그냥 유실
            if time.monotonic() - start > DEADLINE_SECONDS:
                lost += len(chunk)
                print(
                    f"[librarian] 배치 {i} 실패 + 예산 초과 — 재시도 없이 {len(chunk)}건 스킵",
                    file=sys.stderr,
                )
                continue
            print(f"[librarian] 배치 {i}/{len(chunks)} 실패 — 반으로 쪼개 재시도", file=sys.stderr)
            mid = (len(chunk) + 1) // 2
            for j, half in enumerate((chunk[:mid], chunk[mid:]), start=1):
                if not half:
                    continue
                if time.monotonic() - start > DEADLINE_SECONDS:
                    lost += len(half)
                    print(
                        f"[librarian] 배치 {i} 재시도 {j}/2 예산 초과 — {len(half)}건 스킵",
                        file=sys.stderr,
                    )
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
        "끝내고 각 문장을 마침표('.')로 닫는다 — 명사형(개조식) 종결이나 "
        "마침표 없는 종결 금지.\n\n"
        "키워드 규칙: 한국어, 공백 없이 (표지에 #키워드 해시태그로 실린다). "
        "구체적으로 뽑는다 — 사건 유형(개인정보유출사고·신종랜섬웨어·"
        "공급망공격), 대상 업종·제품군(보험사·커널드라이버), 성격·범위"
        "(해외사고·RaaS·제로데이)의 조합. \"금융\"·\"피싱\"·\"보안\"·"
        "\"해킹\" 같은 광범위 한 단어는 금지 — 더 좁힌 명사구로 쓴다"
        "(예: \"피싱\" → \"결제정보탈취피싱\"). 보안 통용 약어"
        "(APT·LLM·RaaS·RCE)만 영문 허용, 그 외는 한국어로 쓴다. AI 관련 "
        "키워드가 있으면 우선 포함한다. 키워드는 항목 본문이 지지하는 것만 쓴다 — "
        "암호화 없는 데이터 유출 협박은 \"랜섬웨어\"가 아니라 "
        "\"데이터협박\"으로 쓴다.\n\n"
        "출력 형식 (설명 텍스트·코드블록 없이 JSON 그 자체):\n"
        '{"briefing": "...", "keywords": ["...", ...]}\n\n'
        "오늘의 항목:\n" + "\n".join(lines)
    )

    # 파일 편집이 필요 없으므로 --allowedTools 없이(도구 불필요)
    proc = _run_claude_json(["--model", MODEL], prompt, 120)
    if proc is None:
        print("[librarian] 총평 실행 실패", file=sys.stderr)
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
