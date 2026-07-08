"""대형 사건·사고 판정기 (realtime 즉시 발송 게이트, 하이브리드).

v22: "긴급" = 쿠팡·SKT 해킹급, 국가적/글로벌 파장 사건·사고만 (사용자
기준 재확인: "정말정말 파급력이 큰 것들만"). 구 기준(KEV/CVSS≥9/긴급
소스)은 폐기 — 그런 항목도 전부 아침 7시 다이제스트로 몰아 보낸다.

판정은 2단:
1. 키워드 게이트 (무료) — config.yaml urgent_gate 키워드가 제목/요약에
   있는 항목만 후보로 좁혀 LLM 호출을 아낀다.
2. headless Claude(sonnet) — 후보가 있을 때만 호출해 3문 체크리스트
   (실제 사고인가 / 주체가 전국민적 인지도인가 / 규모가 대량인가)
   전부 충족 + scale(1~5) 자기평가로 최종 판정. 코드에서
   config urgent_min_scale(기본 5) 미만을 한 번 더 걸러 이중 게이트.
   state/urgent_history.json(최근 발송 이력)을 프롬프트에 줘 같은
   사건의 후속 보도 재울림을 막는다.

실패 정책은 fail-quiet: 토큰 없음/타임아웃/파싱 실패면 아무것도 긴급으로
올리지 않고 다이제스트로 보낸다. 긴급 채널에서는 오탐(사소한 기사가
새벽에 울리는 것)이 미탐(아침에 몰아서 아는 것)보다 나쁘다는 사용자
선호 — 사서(librarian)의 fail-open(전부 전송)과 방향이 반대다.
"""
import datetime
import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_PATH = os.path.join(BASE_DIR, "state", "urgent_history.json")
HISTORY_KEEP_DAYS = 14

TIMEOUT_SECONDS = 120
# haiku가 "대형"을 관대하게 해석해 오탐이 잦았다(2026-07-08 사용자 보고).
# 게이트 통과 시 런당 1콜뿐이라 판정 품질을 우선한다
MODEL = "claude-sonnet-5"
DEFAULT_MIN_SCALE = 5

# config urgent_gate가 비어 있을 때의 기본 게이트 — 사건·사고 어휘만.
# 넓게 잡되(미탐 방지) '취약점'류 일반 단어는 넣지 않는다: 최종 선별은
# 어차피 LLM이 한다
DEFAULT_GATE_KEYWORDS = [
    "유출", "해킹", "침해", "탈취", "마비", "랜섬웨어 감염", "피해",
    "breach", "leak", "hacked", "compromised", "stolen", "exfiltrat",
    "mass exploitation", "under active exploitation",
]

_PROMPT_HEADER = """\
너는 보안 뉴스 긴급도 판정기다. 아래 JSON 항목들 중 **지금 즉시 깨워서
알려야 할 국가적/글로벌 파장의 사건·사고**만 골라라. 기본값은 "긴급
아님"이다 — 하루에 1건도 없는 날이 대부분이어야 정상이다.

다음 3문에 **전부 예**일 때만 긴급이다:
① 실제로 발생했거나 진행 중인 침해·유출·마비 **사고**인가?
   (취약점 공개·패치·PoC·연구·경고·캠페인 분석·정책 발표는 사고가 아니다)
② 피해 주체가 **전국민적/글로벌 인지도**의 기업·기관·인프라인가?
   (대형 통신사·시중은행·쿠팡/네이버급 플랫폼·Claude/OpenAI급 AI 서비스·
   정부기관·전력망/금융망. 이름을 처음 듣는 회사면 아니다)
③ 피해 규모가 **대량**인가? (수십만 건 이상 개인정보, 서비스 전면 마비,
   핵심 소스코드 유출. "가능성"·"정황 조사 중" 단계의 소규모 건은 아니다)

긴급 O 예시: "SKT 유심 정보 해킹, 2천만 가입자 영향" /
"쿠팡 고객정보 대량 유출 확인" / "Anthropic, Claude 사용자 대화 대량 유출"
긴급 X 예시: 개별 제품 CVE 공개(악용 중이어도 주체가 ②급이 아니면 X) /
중소기업·지역기관 침해 / APT 캠페인 분석 리포트 / 이미 알려진 사건의
후속·해설 보도 / 보안업체 연구 발표

**애매하면 긴급이 아니다** — 긴급이 아니어도 아침 다이제스트로 전달되므로
놓치는 것이 아니다. 오탐(사소한 기사로 새벽에 울리는 것)이 미탐보다 나쁘다.
"""

_HISTORY_HEADER = """
최근 발송한 긴급 알림 (같은 사건의 후속·반복·상세 보도는 긴급이 아니다):
"""

_ITEMS_HEADER = """
항목:
"""

_PROMPT_FOOTER = """

응답은 아래 형식의 JSON 하나만 출력한다 (설명·코드블록 없이):
{"urgent": [{"id": "<item id>", "scale": 5, "reason": "긴급 판정 사유 한 줄 (한국어 30자 이내, 예: '국내 금융권 고객정보 대량 유출')"}]}

scale은 파장 자기평가 1~5 정수 — 5 = 국가적/글로벌 파장(위 3문 전부
확실한 예), 4 = 업계 전체 파장, 3 이하 = 긴급 후보 아님(리스트에서 빼라).
긴급 항목이 없으면 {"urgent": []}. reason은 '왜 지금 봐야 하는지'가
한눈에 읽히는 명사구나 짧은 문장으로 쓴다.
"""


def gate_candidates(items: list[dict], config: dict) -> list[dict]:
    keywords = [
        k.lower() for k in (config.get("urgent_gate") or DEFAULT_GATE_KEYWORDS)
    ]
    hits = []
    for item in items:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        if any(k in text for k in keywords):
            hits.append(item)
    return hits


def load_history() -> list[dict]:
    """최근 발송 이력 (없으면 빈 리스트 — fail-open)."""
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            entries = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(entries, list):
        return []
    cutoff = (
        datetime.date.today() - datetime.timedelta(days=HISTORY_KEEP_DAYS)
    ).isoformat()
    return [e for e in entries if isinstance(e, dict) and e.get("date", "") >= cutoff]


def record_history(items: list[dict]) -> None:
    """긴급 발송 성공분을 이력에 적립 (실패해도 알림 흐름은 못 깨뜨린다)."""
    if not items:
        return
    entries = load_history()
    today = datetime.date.today().isoformat()
    for it in items:
        entries.append({
            "date": today,
            "title": (it.get("title") or "")[:120],
            "reason": it.get("urgent_reason", ""),
        })
    try:
        os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=1)
    except OSError as exc:
        print(f"[judge] 이력 기록 실패(무시): {exc}", file=sys.stderr)


def _history_block(entries: list[dict]) -> str:
    if not entries:
        return ""
    lines = [f"- {e['date']} {e['title']}" for e in entries[-20:]]
    return _HISTORY_HEADER + "\n".join(lines) + "\n"


def _judge_input(items: list[dict]) -> str:
    payload = [
        {
            "id": it.get("id"),
            "title": it.get("title"),
            # 요약 전문은 판정에 불필요 — 프롬프트를 짧게 유지
            "summary": (it.get("summary") or "")[:300],
            "source": it.get("source"),
        }
        for it in items
    ]
    return json.dumps(payload, ensure_ascii=False, indent=1)


def _extract_json_object(text: str):
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end < start:
        raise ValueError("no JSON object in judge output")
    return json.loads(text[start:end + 1])


def select_urgent(items: list[dict], config: dict, allow_llm: bool = True) -> list[dict]:
    """대형 사건·사고로 판정된 항목 리스트 (입력 순서 유지).
    allow_llm=False(DRY_RUN)면 게이트 통과 수만 로그로 남기고 빈 리스트."""
    candidates = gate_candidates(items, config)
    if not candidates:
        return []

    if not allow_llm:
        print(f"[judge] DRY_RUN: 게이트 후보 {len(candidates)}건 — LLM 판정 생략", file=sys.stderr)
        return []

    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        print("[judge] CLAUDE_CODE_OAUTH_TOKEN 미설정 — 긴급 판정 스킵(다이제스트로)", file=sys.stderr)
        return []

    prompt = (
        _PROMPT_HEADER
        + _history_block(load_history())
        + _ITEMS_HEADER
        + _judge_input(candidates)
        + _PROMPT_FOOTER
    )
    try:
        proc = subprocess.run(
            [
                # --bare 금지: credentials 파일까지 스킵해 CI에서 인증이 깨진다
                "claude", "-p", prompt,
                "--model", MODEL,
                "--allowedTools", "Read",  # 판정에 도구 불필요 — 최소 허용
                "--output-format", "json",
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[judge] 실행 실패(다이제스트로): {exc}", file=sys.stderr)
        return []

    if proc.returncode != 0:
        print(
            f"[judge] 비정상 종료 (code={proc.returncode}) "
            f"stderr: {proc.stderr[:300]} | stdout: {proc.stdout[:300]}",
            file=sys.stderr,
        )
        return []

    min_scale = int(config.get("urgent_min_scale", DEFAULT_MIN_SCALE))
    try:
        outer = json.loads(proc.stdout)
        result = _extract_json_object(outer["result"])
        # 신형: {"urgent": [{"id", "scale", "reason"}]} — 프롬프트가 3 이하를
        # 빼라고 해도 모델이 어길 수 있어 코드에서 min_scale 미만을 한 번 더
        # 거른다(이중 게이트). scale 누락은 0 취급 = 탈락.
        # 레거시: {"urgent_ids": [...]} — 모델이 구 스키마로 답해도 선별은
        # 유지하되 사유 없이(fail-open: embed는 사유 없어도 렌더된다).
        reasons: dict[str, str] = {}
        scales: dict[str, int] = {}
        if result.get("urgent") is not None:
            for entry in result["urgent"] or []:
                if not (isinstance(entry, dict) and entry.get("id")):
                    continue
                try:
                    scale = int(entry.get("scale") or 0)
                except (TypeError, ValueError):
                    scale = 0
                if scale < min_scale:
                    print(
                        f"[judge] scale {scale} < {min_scale} 탈락: "
                        f"{str(entry.get('reason') or entry['id'])[:60]}",
                        file=sys.stderr,
                    )
                    continue
                # 프롬프트가 30자 이내를 요구하지만 모델이 어길 수 있다 —
                # 폭주한 사유가 embed 본문을 밀어내지 않게 코드에서도 자른다
                reasons[entry["id"]] = str(entry.get("reason") or "").strip()[:50]
                scales[entry["id"]] = scale
            urgent_ids = set(reasons)
        else:
            urgent_ids = set(result.get("urgent_ids") or [])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"[judge] 응답 파싱 실패(다이제스트로): {exc}", file=sys.stderr)
        return []

    # 후보에 없던 id를 지어내도 무시된다 — 게이트 통과분 안에서만 선별
    selected = [it for it in candidates if it.get("id") in urgent_ids]
    for it in selected:
        reason = reasons.get(it.get("id"))
        if reason:
            it["urgent_reason"] = reason
    # 무엇이 왜 울렸는지 로그에 남긴다 — 오탐 튜닝의 근거 데이터
    for it in selected:
        print(
            f"[judge] 긴급: {(it.get('title') or '')[:80]} | "
            f"scale {scales.get(it.get('id'), '?')} | "
            f"{it.get('urgent_reason', '(사유 없음)')}",
            file=sys.stderr,
        )
    if selected:
        print(f"[judge] 대형 사건 판정: {len(selected)}건 즉시 발송", file=sys.stderr)
    return selected
