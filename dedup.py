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
import sys
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


# ------------------------------------------------------- 고유 토큰 사건 판정
# 2026-11-20 QA B1. 제목 자카드는 다른 매체의 같은 사건 보도를 못 잡았고
# (알려진 재게재 4건 중 0건) 유출 사고 상투어 겹침으로 다른 사건을 묶었다
# (KB캐피탈과 한패스, 서울시립대와 국제예술대학교). 사건을 가르는 것은
# 고유명사, 단위 붙은 수치, CVE 번호다. 일반 보안 용어와 사고 상투어는
# 토큰으로 치지 않는다. 발행 원장 결정적 판정과 오늘 후보끼리의 결정적
# 중복 백업이 쓴다.

_NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
_QTY_RE = re.compile(
    r"(?<![\w.\-])(?P<usd>\$\s?)?"
    rf"(?P<num>(?:{_NUM}[조억만천])*{_NUM}[조억만천]?)"
    r"(?P<approx>여)?"
    r"(?:\s?(?P<unit>million|billion|thousand|bn|달러|dollars?|usd|%|퍼센트"
    r"|[mbk](?![A-Za-z])|[년월일시분초]))?",
    re.IGNORECASE,
)
_NUM_PART_RE = re.compile(rf"({_NUM})([조억만천]?)")
_MAG_KO = {"조": 10 ** 12, "억": 10 ** 8, "만": 10 ** 4, "천": 10 ** 3}
_MAG_EN = {"thousand": 10 ** 3, "k": 10 ** 3, "million": 10 ** 6, "m": 10 ** 6,
           "billion": 10 ** 9, "bn": 10 ** 9, "b": 10 ** 9}
_MONTH = (r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?"
          r"|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b")
_MONTH_BEFORE_RE = re.compile(_MONTH + r"\.?\s*$", re.I)
_MONTH_AFTER_RE = re.compile(r"^\s*" + _MONTH, re.I)
# 제품명 뒤 숫자는 버전이다(Microsoft 365, Windows 11, Chrome 142)
_VERSIONED_BEFORE_RE = re.compile(
    r"\b(?:microsoft|office|windows|server|exchange|ios|ipados|android|macos"
    r"|galaxy|iphone|pixel|chrome|firefox|python|java|php|node|ubuntu|debian"
    r"|rhel|fortios|pan-os|junos|version|ver|v|iso|iec|rfc|sp)\s*$", re.I)
_ORDINAL_RE = re.compile(r"\d+(?:st|nd|rd|th)", re.I)

_LATIN_RE = re.compile(
    r"(?<![A-Za-z0-9])[A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*")
_HANGUL_TOKEN_RE = re.compile(r"[가-힣]+")
_LONG_WORD_RE = re.compile(r"[A-Za-z]{4,}")
_SENTENCE_BREAK = set(".!?:;\"'([{|-"
                      "\u2014\u2013\u2018\u2019\u201c\u201d\u00b7\u2026")

# 이름이 아닌 일반 용어와 약어. 대문자로 쓰여도 사건을 가르지 못한다
_GENERIC_NAMES = frozenset("""
ai api apis cve cves cvss cwe rce lpe poc pocs ioc iocs ttp ttps ot ics it iot
vpn vpns apt apts ddos dos xss csrf ssrf sql sqli llm llms mfa 2fa otp sso
ceo cto ciso cso cio us uk eu un usd krw pc os url urls dns http https ssh rdp
smb html pdf json xml zip exe dll sdk cli ui id ids ip ips tls ssl saas paas
iaas edr xdr mdr siem soc waf msp mssp rmm nas rat rats c2 cnc kev nvd ghsa
zero-day zero-days 0-day n-day cyber security data cloud mode update updates
patch patches hotfix flaw flaws bug bugs vulnerability vulnerabilities attack
attacks hacker hackers malware ransomware botnet phishing exploit exploits
backdoor trojan worm infostealer stealer spyware wiper loader dropper threat
threats breach breaches leak incident report new the and for with from after
over says said warns via inc corp ltd co llc gmbh plc pte blog news post
monday tuesday wednesday thursday friday saturday sunday january february
march april june july august september october november december
federal bureau investigation department justice democratic people republic
agency ministry government national united states kingdom view csaf summary
energy electric automation industrial jan feb mar apr may jun jul aug sep sept
oct nov dec mon tue wed thu fri sat sun recorded future ahnlab asec center ca
pki isc sans team group manager product
""".split())
# 흔한 대형 벤더와 기관. 이름으로 치되 작은 수치 하나와 짝지어 판정하지 않는다
_COMMON_NAMES = frozenset("""
microsoft windows office outlook exchange azure google chrome android gmail
apple ios macos iphone linux meta facebook instagram whatsapp amazon aws
cisco oracle ibm intel amd nvidia samsung openai chatgpt gpt anthropic claude
gemini github gitlab npm pypi docker kubernetes fbi cisa nsa doj ncsc kisa nis
europol interpol dprk china chinese russia russian iran iranian north south
korea korean ukraine ukrainian israel usa america american europe european
japan japanese taiwan telegram discord firefox mozilla adobe vmware broadcom
fortinet fortigate ivanti citrix sap salesforce okta cloudflare crowdstrike
sophos kaspersky eset mandiant talos zscaler sentinelone proofpoint siemens
schneider rockwell hitachi mitsubishi abb honeywell moxa kisia kiisc kotra
한국인터넷진흥원 한국정보보호산업협회 정보통신산업진흥원
""".split())
# 한글 기관명 꼬리. 꼬리 앞에 두 글자 이상이 붙어야 고유명으로 본다
_KO_ORG_SUFFIX = (
    "대학교", "대학", "캐피탈", "생명", "화재", "손해보험", "저축은행", "은행",
    "증권", "카드", "공사", "공단", "병원", "그룹", "전자", "텔레콤", "거래소",
    "재단", "협회", "진흥원", "자산운용", "대",
)
_KO_GENERIC_END = (
    "세대", "시대", "확대", "최대", "증대", "극대", "연대", "기대", "반대",
    "상대", "강대", "거대", "막대", "역대", "절대", "국립대", "사립대", "지방대",
    "명문대", "시중은행", "인터넷은행", "지방은행", "중앙은행", "가상자산거래소",
    "암호화폐거래소", "코인거래소", "신용카드", "체크카드", "보안카드", "교통카드",
    "해킹그룹", "공격그룹", "웨어그룹", "위협그룹", "대학병원", "종합병원", "대형화재",
)


def _sig_digits(value: float) -> int:
    return len(str(int(round(value))).rstrip("0")) or 1


def _quantities(text: str) -> list[tuple[str, float]]:
    """단위 붙은 수치 (cls, value). cls는 usd, pct, n.
    날짜, 시각, 연도, 버전, CVSS 점수, 10 미만 개수는 뺀다."""
    out = []
    for m in _QTY_RE.finditer(text):
        num = m.group("num")
        unit = (m.group("unit") or "").lower()
        usd = bool(m.group("usd")) or unit in ("달러", "dollar", "dollars", "usd")
        end = m.end()
        if end < len(text) and text[end].isascii() and text[end].isalnum():
            continue  # 4EverAble2Shell, 2FA, 5G
        if unit and unit in "년월일시분초":
            continue
        if unit in ("m", "b", "k") and not usd:
            continue
        has_mag = any(ch in num for ch in "조억만천") or unit in _MAG_EN
        if "." in num and not has_mag and not usd and unit not in ("%", "퍼센트"):
            continue  # 9.8, 5.4 같은 점수와 버전
        before = text[max(0, m.start() - 20):m.start()]
        if "cvss" in before.lower() or _VERSIONED_BEFORE_RE.search(before):
            continue
        if _MONTH_BEFORE_RE.search(before) or _MONTH_AFTER_RE.match(text[end:end + 12]):
            continue
        value = sum(float(n.replace(",", "")) * _MAG_KO.get(g, 1)
                    for n, g in _NUM_PART_RE.findall(num))
        value *= _MAG_EN.get(unit, 1)
        cls = "usd" if usd else ("pct" if unit in ("%", "퍼센트") else "n")
        if cls == "n" and not unit and re.fullmatch(r"(?:19|20)\d\d", num):
            continue  # 연도
        if cls == "n" and value < 10:
            continue
        out.append((cls, value))
    return out


def _sentence_initial(text: str, start: int) -> bool:
    before = text[:start].rstrip()
    return not before or before[-1] in _SENTENCE_BREAK


def _latin_names(text: str) -> tuple[set[str], set[str]]:
    """라틴 문자 고유명 (전체, 표지). 표지는 모양(대소문자 섞임, 숫자,
    하이픈)이 있거나 한글 문장 속에 쓰인 영문이다. 영어 문장 중간의
    대문자 단어(Uber, Team)는 전체에만 든다. 모든 단어가 대문자로 시작하는
    영어 제목은 모양만 본다."""
    hangul_ctx = bool(_HANGUL_TOKEN_RE.search(text))
    words = _LONG_WORD_RE.findall(text)
    title_case = (not hangul_ctx and len(words) >= 3
                  and sum(w[0].isupper() for w in words) / len(words) > 0.6)
    names, marked = set(), set()
    for m in _LATIN_RE.finditer(text):
        tok = m.group(0)
        if (sum(ch.isalpha() for ch in tok) < 2 or CVE_RE.fullmatch(tok)
                or _ORDINAL_RE.fullmatch(tok)):
            continue
        if re.fullmatch(r"[A-Z]{2,}s", tok):
            tok = tok[:-1]  # MSPs
        low = tok.lower()
        if low in _GENERIC_NAMES:
            continue
        shaped = (any(ch.isdigit() for ch in tok)
                  or any(ch.isupper() for ch in tok[1:])
                  or ("-" in tok and tok[0].isupper()))
        if not shaped:
            if not tok[0].isupper() or title_case:
                continue
            if not hangul_ctx and _sentence_initial(text, m.start()):
                continue
        names.add(low)
        if shaped or hangul_ctx:
            marked.add(low)
    return names, marked


def _korean_org_names(text: str) -> set[str]:
    out = set()
    for raw in _HANGUL_TOKEN_RE.findall(text):
        tok = _strip_josa(raw)
        if tok.endswith("대학교"):
            tok = tok[:-3] + "대"
        elif tok.endswith("대학"):
            tok = tok[:-2] + "대"
        if tok.endswith(_KO_GENERIC_END):
            continue
        suffix = next((s for s in _KO_ORG_SUFFIX if tok.endswith(s)), None)
        if suffix and len(tok) - len(suffix) >= 2:
            out.add(tok)
    return out


def _cluster(qty: list[tuple[str, float]]) -> list[tuple[str, list[float]]]:
    """한 항목 안 같은 수치의 다른 표기(47만, 47만3천)를 한 묶음으로."""
    clusters: list[tuple[str, list[float]]] = []
    for cls, value in sorted(set(qty)):
        last = clusters[-1] if clusters else None
        if last and last[0] == cls and any(_same_figure(v, value) for v in last[1]):
            last[1].append(value)
        else:
            clusters.append((cls, [value]))
    return clusters


def _round_sig(value: float, digits: int) -> float:
    factor = 10 ** (len(str(int(round(value)))) - digits)
    return round(value / factor) * factor


def _same_figure(a: float, b: float) -> bool:
    """같은 수치인가. 정확히 같거나, 유효숫자가 적은 쪽이 다른 쪽의 반올림
    표기일 때(47만과 47만3천, 1,800과 1,811). 10148과 10144는 다르다.
    천 미만 작은 수(15와 20)와 유효숫자 한 자리 표기(3만과 27001)는
    반올림으로 묶지 않는다."""
    if abs(a - b) < 1e-9 * max(a, b, 1):
        return True
    coarse, fine = sorted((a, b), key=_sig_digits)
    digits = _sig_digits(coarse)
    if digits == _sig_digits(fine) or digits < 2 or coarse < 1000:
        return False
    return abs(_round_sig(fine, digits) - coarse) < 1e-9 * max(coarse, 1)


def story_tokens(item: dict) -> dict:
    """사건 판정용 고유 토큰. 원제, 한국어 제목, 원문 요약, 한국어 요약 전부."""
    fields = [item.get(k) or "" for k in ("title", "title_ko", "summary", "summary_ko")]
    fields = [f.replace("**", "") for f in fields if isinstance(f, str)]
    qty: list[tuple[str, float]] = []
    names: set[str] = set()
    marked: set[str] = set()
    for text in fields:
        qty.extend(_quantities(text))
        latin, latin_marked = _latin_names(text)
        korean = _korean_org_names(text)
        names |= latin | korean
        marked |= latin_marked | korean
    return {
        "cves": extract_cves(" ".join(fields)),
        "qty": _cluster(qty),
        "names": names,
        "marked": marked,
    }


def _qty_strong(cls: str, values: list[float]) -> bool:
    """통화 금액이거나, 100 이상이면서 유효숫자 두 자리 이상(948, 1,811, 47만)."""
    return cls == "usd" or any(v >= 100 and _sig_digits(v) >= 2 for v in values)


def story_overlap(ta: dict, tb: dict, same_day: bool = False) -> str | None:
    """두 토큰 묶음이 같은 사건이면 근거 문자열, 아니면 None.

    날짜를 넘는 비교(기본):
      CVE 공유, 또는
      강한 수치 하나 + (다른 수치 또는 이름 하나), 또는
      약한 수치 하나 + 대형 벤더가 아닌 표지 이름 하나.
    이름만 겹치는 경우는 같은 사건의 후속 보도(패치 공개 등)와 구분이
    안 되므로 날짜를 넘을 때는 같은 사건으로 보지 않는다.
    같은 날 후보끼리(same_day)는 대형 벤더가 아닌 표지 이름 두 개 공유도
    같은 사건이다. 같은 날 두 매체 보도는 후속이 아니라 중복이다."""
    cves = ta["cves"] & tb["cves"]
    if cves:
        return "CVE " + ", ".join(sorted(cves))
    used: set[int] = set()
    strong, weak = [], []
    for cls, values in ta["qty"]:
        for j, (cls_b, values_b) in enumerate(tb["qty"]):
            if j in used or cls != cls_b:
                continue
            if any(_same_figure(a, b) for a in values for b in values_b):
                used.add(j)
                shown = f"{max(values):g}" + ("$" if cls == "usd" else "")
                (strong if _qty_strong(cls, values + values_b) else weak).append(shown)
                break
    names = ta["names"] & tb["names"]
    rare = (ta["marked"] & tb["marked"]) - _COMMON_NAMES
    reason = f"수치 {strong + weak} 이름 {sorted(names)}"
    if strong and (len(strong) + len(weak) >= 2 or names):
        return reason
    if weak and rare:
        return reason
    if same_day and len(rare) >= 2:
        return reason
    return None


def is_same_story(a: dict, b: dict, same_day: bool = False) -> bool:
    return story_overlap(story_tokens(a), story_tokens(b), same_day) is not None


def dedup_today(candidates: list[dict]) -> tuple[list[dict], list[dict]]:
    """오늘 후보끼리의 결정적 중복 제거. LLM 중복 게이트가 실패했을 때의
    백업이다. 입력 순서(순위)가 앞선 항목이 남는다.
    반환 (kept, dropped). dropped 항목은 남은 항목과 같은 사건이라 소진한다."""
    kept: list[dict] = []
    kept_tokens: list[dict] = []
    dropped: list[dict] = []
    for item in candidates:
        tokens = story_tokens(item)
        hit = next(((k, why) for k, kt in zip(kept, kept_tokens)
                    if (why := story_overlap(tokens, kt, same_day=True))), None)
        if hit:
            print(f"[dedup] 같은 날 같은 사건 제외: {item.get('title_ko') or item.get('title')} "
                  f"(대표: {hit[0].get('title_ko') or hit[0].get('title')}, {hit[1]})",
                  file=sys.stderr)
            dropped.append(item)
            continue
        kept.append(item)
        kept_tokens.append(tokens)
    return kept, dropped
