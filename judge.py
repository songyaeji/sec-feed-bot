"""대형 사건·사고 판정기 (realtime 즉시 발송 게이트, 하이브리드).

v8: "긴급" = SKT 해킹 사고, 대규모 소스코드·개인정보 유출급의
국가적/업계 파장 사건·사고만. 구 기준(KEV/CVSS≥9/긴급 소스)은 폐기 —
그런 항목도 전부 아침 7시 다이제스트로 몰아 보낸다 (사용자 결정).

판정은 2단:
1. 키워드 게이트 (무료) — config.yaml urgent_gate 키워드가 제목/요약에
   있는 항목만 후보로 좁혀 LLM 호출을 아낀다.
2. headless Claude(haiku) — 후보가 있을 때만 호출해 "파장급 사건"인지
   최종 판정한다.

실패 정책은 fail-quiet: 토큰 없음/타임아웃/파싱 실패면 아무것도 긴급으로
올리지 않고 다이제스트로 보낸다. 긴급 채널에서는 오탐(사소한 기사가
새벽에 울리는 것)이 미탐(아침에 몰아서 아는 것)보다 나쁘다는 사용자
선호 — 사서(librarian)의 fail-open(전부 전송)과 방향이 반대다.
"""
import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TIMEOUT_SECONDS = 120
MODEL = "claude-haiku-4-5-20251001"

# config urgent_gate가 비어 있을 때의 기본 게이트 — 사건·사고 어휘만.
# 넓게 잡되(미탐 방지) '취약점'류 일반 단어는 넣지 않는다: 최종 선별은
# 어차피 LLM이 한다
DEFAULT_GATE_KEYWORDS = [
    "유출", "해킹", "침해", "탈취", "마비", "랜섬웨어 감염", "피해",
    "breach", "leak", "hacked", "compromised", "stolen", "exfiltrat",
    "mass exploitation", "under active exploitation",
]

_PROMPT_HEADER = """\
너는 보안 뉴스 긴급도 판정기다. 아래 JSON 항목들 중 **지금 즉시 알려야
할 대형 사건·사고**만 골라라.

긴급의 기준 (전부 이 수준이어야 한다):
- 대형 기업·기관·인프라의 실제 침해/해킹 사고 (예: 대형 통신사 해킹,
  주요 서비스 소스코드·대규모 개인정보 유출, 금융망·전력망 마비)
- 국가적 또는 업계 전체에 파장이 있는 사건
- CVE라면: 광범위하게 배포된 제품이 실제 대규모 악용 중이어서 즉시
  조치가 필요한 경우만

긴급이 아닌 것: 일반 취약점 공개·패치, 소규모/개인 대상 캠페인, 분석
리포트, 제품·행사 소식, 과거 사건의 후속 보도. **애매하면 긴급이 아니다**
— 긴급이 아니면 아침 다이제스트로 전달되므로 놓치는 것이 아니다.

항목:
"""

_PROMPT_FOOTER = """

응답은 아래 형식의 JSON 하나만 출력한다 (설명·코드블록 없이):
{"urgent": [{"id": "<item id>", "reason": "긴급 판정 사유 한 줄 (한국어 30자 이내, 예: '국내 금융권 고객정보 대량 유출')"}]}

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

    prompt = _PROMPT_HEADER + _judge_input(candidates) + _PROMPT_FOOTER
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

    try:
        outer = json.loads(proc.stdout)
        result = _extract_json_object(outer["result"])
        # 신형: {"urgent": [{"id", "reason"}]} — id→사유 매핑으로 embed에 전달.
        # 레거시: {"urgent_ids": [...]} — 모델이 구 스키마로 답해도 선별은
        # 유지하되 사유 없이(fail-open: embed는 사유 없어도 렌더된다).
        reasons: dict[str, str] = {}
        if result.get("urgent") is not None:
            for entry in result["urgent"] or []:
                if isinstance(entry, dict) and entry.get("id"):
                    # 프롬프트가 30자 이내를 요구하지만 모델이 어길 수 있다 —
                    # 폭주한 사유가 embed 본문을 밀어내지 않게 코드에서도 자른다
                    reasons[entry["id"]] = str(entry.get("reason") or "").strip()[:50]
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
    if selected:
        print(f"[judge] 대형 사건 판정: {len(selected)}건 즉시 발송", file=sys.stderr)
    return selected
