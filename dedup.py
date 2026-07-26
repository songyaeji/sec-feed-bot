"""1st-layer heuristic cross-source duplicate detection.

main.dedup() (id-based) only catches a literal re-fetch of the same URL/CVE
id. This module catches the same *event* being reported a second time by a
different outlet -- e.g. NVD's own CVE-2026-XXXXX entry followed a day later
by a news site's "OO사, XX 취약점 패치" article about the same CVE, or two
news sites covering the same breach with different headlines and no CVE at
all.

State lives in state/seen.json alongside the existing "seen"/"last_run"
fields (see ensure_dedup_state for backward compatibility with older
seen.json files that don't have these keys yet):

  "alerted_cves":  {CVE_ID: first_alert_iso}   -- pruned after 90 days
  "recent_titles": [{"t": normalized_title, "d": iso}]  -- pruned after 7 days
"""
import re
from datetime import datetime, timedelta, timezone

CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
_TOKEN_RE = re.compile(r"[a-z0-9가-힣]+")

ALERTED_CVE_TTL_DAYS = 90
RECENT_TITLE_TTL_DAYS = 7
TITLE_JACCARD_THRESHOLD = 0.6


def extract_cves(text: str) -> set[str]:
    if not text:
        return set()
    return {m.group(0).upper() for m in CVE_RE.finditer(text)}


# 한국어 조사 — 같은 명사가 조사 때문에 다른 토큰이 되면 자카드가 깎인다
# (2026-07-26 NO.19 실측: "에이전트," vs "에이전트로" 때문에 0.4 → 카드 2장).
# 긴 것부터 벗겨야 "으로"가 "로"보다 먼저 걸린다.
_JOSA = (
    "으로부터", "에게서", "으로써", "에서는", "에게는", "으로", "에서", "에게",
    "부터", "까지", "라는", "이라", "과의", "와의", "의", "은", "는", "이",
    "가", "을", "를", "로", "에", "과", "와", "도", "만",
)
# 조사를 뗀 뒤 남는 어간의 최소 길이 — 2음절 명사가 조사로 오인돼 잘리는
# 사고를 막는다("평가"→"평", "정의"→"정", "국가"→"국"은 전부 미절단)
_MIN_STEM_LEN = 2


def _strip_josa(token: str) -> str:
    if not ("가" <= token[0] <= "힣"):  # 한글 토큰만 대상(영문 어미는 손대지 않음)
        return token
    for josa in _JOSA:
        if token.endswith(josa) and len(token) - len(josa) >= _MIN_STEM_LEN:
            return token[: -len(josa)]
    return token


def _normalize_title(title: str) -> str:
    # lowercase, keep only alphanumerics + hangul, tokenize -- this throws
    # away punctuation/particles differences between two outlets' headlines
    # about the same story so the jaccard comparison isn't thrown off by
    # e.g. one using a colon and the other a dash
    return " ".join(_strip_josa(t) for t in _TOKEN_RE.findall(title.lower()))


def _item_cves(item: dict) -> set[str]:
    text = f"{item.get('title', '')} {item.get('summary', '')}"
    return extract_cves(text)


def ensure_dedup_state(state: dict) -> None:
    """Mutate state in place so a seen.json written before this feature
    existed gets the new keys instead of KeyError'ing downstream."""
    state.setdefault("alerted_cves", {})
    state.setdefault("recent_titles", [])


def is_cross_duplicate(item: dict, state: dict) -> bool:
    ensure_dedup_state(state)
    cves = _item_cves(item)

    if cves:
        # only a duplicate if EVERY CVE mentioned has already been alerted;
        # an item that adds even one new CVE to the conversation is new news
        return cves.issubset(state["alerted_cves"].keys())

    normalized = _normalize_title(item.get("title", ""))
    tokens = set(normalized.split())
    if not tokens:
        return False

    cutoff = datetime.now(timezone.utc) - timedelta(days=RECENT_TITLE_TTL_DAYS)
    for entry in state["recent_titles"]:
        try:
            entry_dt = datetime.fromisoformat(entry["d"])
        except (KeyError, TypeError, ValueError):
            continue
        if entry_dt < cutoff:
            continue
        other_tokens = set(entry.get("t", "").split())
        if not other_tokens:
            continue
        union = tokens | other_tokens
        if union and len(tokens & other_tokens) / len(union) >= TITLE_JACCARD_THRESHOLD:
            return True
    return False


def record_alerted(item: dict, state: dict, now: datetime = None) -> None:
    """Record an item that passed the cross-duplicate filter (whether it
    ends up as an individual card, in pending.json, or in a digest) so a
    later re-report of the same event is caught even if this one hasn't
    been flushed to Discord yet."""
    ensure_dedup_state(state)
    now = now or datetime.now(timezone.utc)
    now_iso = now.isoformat()

    for cve in _item_cves(item):
        state["alerted_cves"].setdefault(cve, now_iso)

    normalized = _normalize_title(item.get("title", ""))
    if normalized:
        state["recent_titles"].append({"t": normalized, "d": now_iso})


def prune_dedup_state(state: dict, now: datetime = None) -> None:
    ensure_dedup_state(state)
    now = now or datetime.now(timezone.utc)

    cve_cutoff = now - timedelta(days=ALERTED_CVE_TTL_DAYS)
    pruned_cves = {}
    for cve, first_alert in state["alerted_cves"].items():
        try:
            dt = datetime.fromisoformat(first_alert)
        except (TypeError, ValueError):
            continue
        if dt >= cve_cutoff:
            pruned_cves[cve] = first_alert
    state["alerted_cves"] = pruned_cves

    title_cutoff = now - timedelta(days=RECENT_TITLE_TTL_DAYS)
    pruned_titles = []
    for entry in state["recent_titles"]:
        try:
            dt = datetime.fromisoformat(entry.get("d"))
        except (TypeError, ValueError):
            continue
        if dt >= title_cutoff:
            pruned_titles.append(entry)
    state["recent_titles"] = pruned_titles


TITLE_SIMILARITY_THRESHOLD = 0.5
# 포함관계(containment) 백스톱 — 짧은 제목이 긴 제목에 거의 통째로 들어가면
# 자카드는 길이 차 때문에 낮게 나온다(2026-07-26 실측: "hermes ai agent used
# to automate attack on thai finance ministry" ⊂ "hacker runs hermes ai agent
# unattended for post exploitation at thai finance ministry" = 자카드 0.4,
# 포함률 0.75). 자카드 임계값은 내리지 않고(오탐으로 진짜 뉴스가 조용히
# 버려짐 — 사용자 합의) 겹침이 압도적일 때만 추가로 잡는다.
TITLE_CONTAINMENT_THRESHOLD = 0.75
# 포함률 규칙 적용 조건 — 짧은 제목끼리 우연히 겹치는 오탐 방지
CONTAINMENT_MIN_SHARED = 4
CONTAINMENT_MIN_TOKENS = 5


def _titles_match(ta: set[str], tb: set[str]) -> bool:
    if not (ta and tb):
        return False
    shared = len(ta & tb)
    if shared / len(ta | tb) >= TITLE_SIMILARITY_THRESHOLD:
        return True
    shorter = min(len(ta), len(tb))
    return (
        shorter >= CONTAINMENT_MIN_TOKENS
        and shared >= CONTAINMENT_MIN_SHARED
        and shared / shorter >= TITLE_CONTAINMENT_THRESHOLD
    )


def is_similar_event(a: dict, b: dict) -> bool:
    """두 항목이 같은 사건을 다루는지에 대한 결정적 판정 — 카드 최종 선별
    단계의 교차 소스 중복 백스톱(main._dedup_similar). CVE 교집합이 있으면
    같은 사건으로 보고, 아니면 제목 토큰 자카드 유사도 또는 포함률로 판정한다.
    영어 매체 2곳은 title끼리, 국내·해외 교차 보도는 사서 번역(title_ko)
    끼리 겹치므로 두 키를 각각 비교한다."""
    cves_a, cves_b = _item_cves(a), _item_cves(b)
    if cves_a and cves_b and cves_a & cves_b:
        return True
    for key in ("title", "title_ko"):
        ta = set(_normalize_title(a.get(key) or "").split())
        tb = set(_normalize_title(b.get(key) or "").split())
        if _titles_match(ta, tb):
            return True
    return False
