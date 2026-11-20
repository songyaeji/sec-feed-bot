"""발송 직전 가이드라인 게이트 (preflight).

digest 카드뉴스가 실제로 나가기 전에, 운영 가이드라인 준수 여부를
결정적(deterministic)으로 점검한다 — LLM·네트워크 없이 stdlib만 쓴다.

점검 근거가 되는 가이드라인:
- 카드·링크는 정말 중요한 것만 소수 (config max_news_items + max_cve_items 상한)
- 카드는 전면 한국어 (card_editor가 title_ko/summary_ko 재작성·검증)
- 뉴스 장수는 가변 — 못 채우면 그날은 적게(2026-11-20 사용자 결정)
- Discord 웹훅 제약: 메시지당 첨부 10개, 파일 8MB
  (출처: Discord Developer Docs — Uploading Files / message limits)
- 비밀정보(웹훅 URL 등) 유출 금지
- 링크 줄과 카드 번호 1:1 대응 (cardgen.build_link_lines 순서 보장)

fatal이 하나라도 있으면 호출자(main.py)는 카드뉴스 발송을 중단하고
기존 텍스트 다이제스트로 폴백해야 한다. warnings는 로그만 남긴다.
"""
import os
import re

import cardgen

# Discord 웹훅 하드 리밋 — 초과 시 API가 요청 자체를 거부한다
DISCORD_MAX_ATTACHMENTS = 10
DISCORD_MAX_FILE_BYTES = 8 * 1024 * 1024

# 송출 텍스트(링크 줄, 브리핑, 카드 문안)에 섞이면 곧 자격증명 유출인 형태.
# 웹훅 URL은 경로에 토큰을 품는다. GitHub 토큰 접두어는 GitHub 문서 기준
# (ghp_ gho_ ghu_ ghs_ ghr_ github_pat_). sk-ant-는 Anthropic API 키와
# setup-token OAuth 토큰의 접두어다
_SECRET_PATTERNS = (
    ("Discord 웹훅", re.compile(r"discord(?:app)?\.com/api/(?:v\d+/)?webhooks/", re.I)),
    ("GitHub 토큰", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("Anthropic 토큰", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{16,}")),
    ("Bearer 토큰", re.compile(r"\bbearer\s+[A-Za-z0-9\-._~+/]{20,}=*", re.I)),
    ("Authorization 헤더", re.compile(r"\bauthorization\s*:\s*\S+\s+[A-Za-z0-9\-._~+/]{16,}=*", re.I)),
)
# 실제 비밀값 대조용 환경변수. 값이 짧으면 오탐이 나 12자 이상만 본다
_SECRET_ENV_VARS = (
    "DISCORD_WEBHOOK_URL", "DISCORD_TREND_WEBHOOK_URL", "CLAUDE_CODE_OAUTH_TOKEN",
    "ANTHROPIC_API_KEY", "NVD_API_KEY", "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET",
    "IG_ACCESS_TOKEN", "GITHUB_TOKEN", "GH_TOKEN", "PORTFOLIO_DEPLOY_KEY",
)
_SECRET_MIN_LEN = 12
# 카드에 그려지는 항목 필드(cardgen이 쓰는 문안과 출처, 링크)
_CARD_TEXT_FIELDS = ("title_ko", "title", "summary_ko", "summary", "why_ko", "term_ko",
                     "tags_ko", "tags", "source", "url")

_HANGUL_RE = re.compile(r"[가-힣]")
_URL_RE = re.compile(r"https?://")

# 정상 카드 구성은 표지 1 + 뉴스 1~7 + 목록 0~1 + '오늘의 CVE' 1 = 3~10장
# (2026-11-20 가변 장수 — 뉴스가 적은 날은 장수가 줄어든다).
# 이 범위를 벗어나면 렌더 로직 이상 신호로 보고 경고만 남긴다
_EXPECTED_PNG_MIN = 2
_EXPECTED_PNG_MAX = 10

_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _noun_ending_count(text: str) -> int:
    """완결형 종결어미('~다')로 끝나지 않거나 마침표로 닫히지 않은 문장 수 —
    개조식 본문·종결 부호 누락 감지. librarian의 교정 게이트가
    실패(fail-open)한 항목을 발송 전에 드러낸다."""
    plain = (text or "").replace("**", "").strip()
    if not plain:
        return 0
    n = 0
    # 전체 텍스트가 마침표로 닫히지 않으면 마지막 문장 종결 부호 누락 1건
    if not plain.endswith("."):
        n += 1
    for sent in _SENT_SPLIT_RE.split(plain):
        sent = sent.strip().rstrip('.!?"\')』」]')
        if sent and not sent.endswith("다"):
            n += 1
    return n


def _outgoing_texts(link_lines: list[str], items: list[dict], briefing: str | None) -> list[str]:
    texts = [t for t in link_lines if isinstance(t, str)]
    if isinstance(briefing, str):
        texts.append(briefing)
    for it in items:
        for key in _CARD_TEXT_FIELDS:
            value = it.get(key)
            if isinstance(value, str):
                texts.append(value)
            elif isinstance(value, (list, tuple)):
                texts.extend(v for v in value if isinstance(v, str))
    return texts


def find_secrets(texts) -> list[str]:
    """비밀값으로 보이는 것의 종류 목록. 값 자체는 돌려주지 않는다(로그 유출 방지)."""
    env_values = [v for v in (os.environ.get(name) for name in _SECRET_ENV_VARS)
                  if v and len(v) >= _SECRET_MIN_LEN]
    found: list[str] = []
    for text in texts:
        if not isinstance(text, str) or not text:
            continue
        for label, pattern in _SECRET_PATTERNS:
            if label not in found and pattern.search(text):
                found.append(label)
        if "환경변수 비밀값" not in found and any(v in text for v in env_values):
            found.append("환경변수 비밀값")
    return found


def check_card_news(
    pngs: list[bytes],
    link_lines: list[str],
    items: list[dict],
    briefing: str | None,
    config: dict,
) -> tuple[list[str], list[str]]:
    """발송 전 결정적(deterministic) 점검. (fatal, warnings) 반환.

    fatal 있으면 카드뉴스 발송을 중단해야 한다(호출자가 텍스트 폴백).
    warnings는 로그만 남기고 발송은 진행한다."""
    fatal: list[str] = []
    warnings: list[str] = []

    # --- FATAL: Discord 첨부 제약 -------------------------------------
    if not pngs:
        fatal.append("카드 PNG가 0장 — 렌더 결과가 비어 있어 보낼 것이 없음")
    elif len(pngs) > DISCORD_MAX_ATTACHMENTS:
        fatal.append(
            f"카드 PNG {len(pngs)}장 — Discord 메시지당 첨부 상한 {DISCORD_MAX_ATTACHMENTS}개 초과"
        )

    bad_size = [
        i for i, png in enumerate(pngs, start=1)
        if len(png) == 0 or len(png) > DISCORD_MAX_FILE_BYTES
    ]
    if bad_size:
        fatal.append(
            f"PNG 크기 이상 {len(bad_size)}장(번호 {bad_size}) — 0바이트 또는 8MB 초과로 업로드 불가"
        )

    # --- FATAL: 선별 상한(가이드라인 '정말 중요한 것만 소수') ----------
    # v16: 뉴스·CVE 상한 분리 — 총량은 두 상한의 합
    max_items = (config.get("max_news_items", 7)
                 + config.get("max_cve_items", 10))
    if len(items) > max_items:
        fatal.append(
            f"발송 항목 {len(items)}건 — 상한 max_news_items+max_cve_items={max_items} "
            f"초과(선별 로직 버그 의심)"
        )

    # --- FATAL: 카드 번호 ↔ 링크 줄 1:1 대응 ---------------------------
    if len(link_lines) != len(items):
        fatal.append(
            f"링크 줄 {len(link_lines)}개 ≠ 항목 {len(items)}건 — 카드 번호와 원문 링크가 어긋남"
        )

    # --- FATAL: 비밀값 유출 방어 -------------------------------------------
    # 링크 줄, 브리핑, 카드 문안 전부를 토큰 형태와 실제 비밀값으로 대조한다
    found = find_secrets(_outgoing_texts(link_lines, items, briefing))
    if found:
        fatal.append(
            f"비밀값 노출 의심 {len(found)}종({', '.join(found)}) — 송출 텍스트에 자격증명 형태 포함"
        )

    # --- FATAL: 링크 없는 링크 줄 ---------------------------------------
    no_url = [i for i, line in enumerate(link_lines, start=1) if not _URL_RE.search(line)]
    if no_url:
        fatal.append(
            f"원문 링크 없는 줄 {len(no_url)}개(번호 {no_url}) — http/https URL이 없어 원문 추적 불가"
        )

    # --- FATAL: 전면 한국어 -----------------------------------------------
    # 2026-11-20: 원문 백필이 폐지돼 모든 카드 항목은 card_editor 검증을
    # 통과한 한국어 문안을 가져야 한다. 여기 걸리면 선별·재작성 경로에
    # 원문이 새는 버그다 — 영어 원문 카드를 내보내느니 발송을 막는다
    no_ko = [
        it.get("id") for it in items
        if not (it.get("title_ko") and _HANGUL_RE.search(it["title_ko"]))
    ]
    if no_ko:
        fatal.append(f"한국어 제목 없는 항목 {len(no_ko)}건: {no_ko}")
    no_summary = [
        it.get("id") for it in items
        if not cardgen.is_cve_lane(it) and not it.get("summary_ko")
    ]
    if no_summary:
        fatal.append(f"한국어 요약 없는 뉴스 {len(no_summary)}건: {no_summary}")

    # --- WARNING: 개조식(명사형 종결) 요약 — 뉴스 카드 본문은 완결형 문장이어야 한다
    bad_style_ids = [
        it.get("id") for it in items
        if not cardgen.is_cve_lane(it)
        and it.get("summary_ko") and _noun_ending_count(it["summary_ko"])
    ]
    if bad_style_ids:
        warnings.append(
            f"개조식 요약 {len(bad_style_ids)}건: {bad_style_ids}"
        )

    # --- WARNING: 표지 브리핑 부재 --------------------------------------
    if not briefing:
        warnings.append("표지 총평(briefing)이 비어 있음 — librarian.summarize 실패 의심")

    # --- WARNING: 카드 장수 이상 범위 ------------------------------------
    if pngs and not (_EXPECTED_PNG_MIN <= len(pngs) <= _EXPECTED_PNG_MAX):
        warnings.append(
            f"카드 PNG {len(pngs)}장 — 예상 범위({_EXPECTED_PNG_MIN}~{_EXPECTED_PNG_MAX}장) 밖(렌더 구성 이상 의심)"
        )
    return fatal, warnings
