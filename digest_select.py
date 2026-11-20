"""digest 카드 선별 로직 — 오늘 후보끼리의 결정적 중복 제거 2겹
(_dedup_by_topic, _dedup_similar)·신선도(_split_fresh)·감점(_author_penalty)·
회차(_issue_no)·순위 점수(_rank_score)·취약점 권고 소스 판별(_is_vuln_source).
사서 입력 컷은 librarian_cut이 맡는다. 같은 사건 묶기, 소스당 상한, 구글뉴스
대리 소스 판별, 사서 실패 경로용 규칙 분류(classify_kind_fallback)를 포함한다.
날짜를 넘는 중복은 published_ledger가 맡는다."""
import re
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import cardgen
import dedup as dedup_lib


def _author_penalty(item: dict, config: dict) -> int:
    # deprioritize_authors 규칙에 걸리는 바이라인이면 importance 감점폭을 돌려준다.
    # 여러 규칙에 걸리면 가장 큰 penalty만 적용(중복 감점 안 함)
    author = item.get("author") or ""
    source = item.get("source") or ""
    pen = 0
    for rule in config.get("deprioritize_authors", []):
        rule_source = rule.get("source")
        if rule_source and rule_source != source:
            continue
        needle = rule.get("author_contains")
        if needle and needle in author:
            pen = max(pen, int(rule.get("penalty", 1)))
    return pen


def _source_regions(config: dict) -> dict[str, str]:
    # 카드 국내/해외 pill — config sources[].region ("국내"/"해외").
    # 미지정 소스는 맵에서 빠져 카드에서 표기를 생략한다
    return {
        s.get("name"): s["region"]
        for s in config.get("sources", [])
        if s.get("region")
    }


def _dedup_by_topic(items: list[dict], verdicts: dict) -> list[dict]:
    """같은 위키 토픽(slug)에 매인 카드 후보가 2건 이상이면 1건만 남긴다.

    사서 LLM이 같은 사건의 교차 소스 보도를 skip_duplicate로 못 걸러도
    (GodDamn/PoisonX 2026-07-10 사례: THN·Security Affairs 각각 new/update
    판정 → 카드 2장) topic slug는 같게 주므로, 여기서 결정적으로 차단한다.
    생존자는 카드 정렬 기준과 동일한 (-importance, -heuristic_score) 우선.
    slug가 유효한 문자열이 아니면(null/누락) 판단 근거가 없으므로 그대로
    통과시킨다 — 사서 출력 불량이 카드를 지우면 안 된다(fail-open)."""
    best_by_topic: dict[str, dict] = {}
    dup_counts: dict[str, int] = {}
    for item in items:
        topic = verdicts.get(item["id"], {}).get("topic")
        if not (isinstance(topic, str) and topic.strip()):
            continue
        topic = topic.strip()
        current = best_by_topic.get(topic)
        if current is None:
            best_by_topic[topic] = item
            continue
        dup_counts[topic] = dup_counts.get(topic, 0) + 1
        challenger_key = (-item.get("importance", 3), -cardgen.heuristic_score(item))
        current_key = (-current.get("importance", 3), -cardgen.heuristic_score(current))
        if challenger_key < current_key:
            best_by_topic[topic] = item

    for topic, count in dup_counts.items():
        print(
            f"[main] 같은 토픽 카드 중복 {count}건 제외 (topic={topic})",
            file=sys.stderr,
        )

    winners = {id(it) for it in best_by_topic.values()}

    def _keep(item: dict) -> bool:
        topic = verdicts.get(item["id"], {}).get("topic")
        if not (isinstance(topic, str) and topic.strip()):
            return True  # topic 없음 — fail-open 통과
        return id(item) in winners

    return [it for it in items if _keep(it)]


def _split_fresh(items: list[dict], seen: dict, ttl_days: int) -> tuple[list[dict], int]:
    """pending TTL — seen 최초 목격이 ttl_days보다 오래된 항목을 걸러낸다.
    카드뉴스는 일간 동향이라 며칠씩 이월된 무판정 꼬리는 카드 가치가 없고,
    이월 무한 누적(사서 예산 재초과 → 뉴스 유실 재발)의 원인이 된다.
    이번 run에서 처음 본 항목은 seen에 아직 없다 — 신선 취급."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=ttl_days)
    fresh: list[dict] = []
    stale = 0
    for item in items:
        first_seen = seen.get(item.get("id"))
        if first_seen:
            try:
                if datetime.fromisoformat(first_seen) < cutoff:
                    stale += 1
                    continue
            except (TypeError, ValueError):
                pass
        fresh.append(item)
    return fresh, stale


def _dedup_similar(items: list[dict]) -> list[dict]:
    """결정적 유사 사건 dedup — CVE 교집합 또는 제목(원문·한국어) 토큰
    유사도로 같은 사건의 교차 소스 보도를 걸러낸다. topic slug 백스톱
    (_dedup_by_topic)은 사서가 두 배치에서 다른 slug를 주면 뚫린다
    (2026-07 사용자 보고: 같은 내용 카드 2장) — slug와 무관한 최종
    방어선. 중요도 상위가 생존한다."""
    kept: list[dict] = []
    for item in sorted(
        items,
        key=lambda it: (-(it.get("importance") or 0), -cardgen.heuristic_score(it)),
    ):
        dup = next((k for k in kept if dedup_lib.is_similar_event(item, k)), None)
        if dup is not None:
            print(
                f"[main] 유사 사건 카드 중복 제외: {item.get('title_ko') or item.get('title')} "
                f"(대표: {dup.get('title_ko') or dup.get('title')})",
                file=sys.stderr,
            )
            continue
        kept.append(item)
    return kept


def _fallback_keywords(items: list[dict], limit: int = 4) -> list[str]:
    # 사서가 keywords를 못 준 날의 표지 해시태그 — 태그 빈도 상위로 대체
    counts: dict[str, int] = {}
    for item in items:
        for tag in item.get("tags") or []:
            counts[tag] = counts.get(tag, 0) + 1
    return [t for t, _ in sorted(counts.items(), key=lambda x: -x[1])[:limit]]


# 날짜 기반 회차의 기본 기준일 — NO.1 = 2026-07-08, NO.5 = 07-12, NO.6 = 07-13.
# config issue_epoch("YYYY-MM-DD")로 조정 가능.
DEFAULT_ISSUE_EPOCH = "2026-07-08"


def _issue_no(config: dict, now_kst: datetime) -> int:
    """발행 회차 = (KST 오늘 - 기준일) + 1. 날짜의 순수 함수라 같은 날
    몇 번을 재발행해도 항상 같은 번호가 나온다(사용자 결정 — 구 카운터
    방식은 재발행마다 번호를 소모했다). 기준일 파싱 실패는 기본값 폴백."""
    raw = str(config.get("issue_epoch") or DEFAULT_ISSUE_EPOCH)
    try:
        epoch = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        epoch = datetime.strptime(DEFAULT_ISSUE_EPOCH, "%Y-%m-%d").date()
    return (now_kst.date() - epoch).days + 1


# 사서가 매기는 기사 성격(kind) — librarian_prompt.md와 같은 목록.
# 뉴스 카드 = 사고·법제도·기관 발표(config card_news_kinds), 취약점은
# 오늘의 CVE 코너, 기타(홍보·실적·행사·칼럼)는 카드에서 제외
KNOWN_KINDS = {"incident", "policy", "institution", "vuln", "other"}


def _is_vuln_source(item: dict, config: dict) -> bool:
    """취약점 권고 전용 소스(config vuln_advisory_sources) 여부 — 이 소스
    항목은 사서 판정과 무관하게 뉴스 카드에 오르지 않는다(사용자 결정
    2026-11-20: 단순 취약점 권고는 오늘의 CVE 코너로)."""
    return item.get("source") in set(config.get("vuln_advisory_sources") or [])


def is_news_proxy(item: dict) -> bool:
    """구글뉴스 쿼리로 기관 이름을 검색해 모은 언론 기사인지.

    이런 항목은 기관 원문이 아니라 여러 매체 기사다. 기관 가중치를 받으면
    사서 입력 상위를 독식한다(2026-11-20 QA: 상위 60 중 48). 링크 호스트
    (news.google.com)로 판별한다. outlet 필드 도입 전에 쌓인 이월 항목도
    같은 기준으로 잡힌다."""
    try:
        host = urlparse(item.get("url") or "").hostname or ""
    except ValueError:
        return False
    return host == "news.google.com"


def _number(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _rank_score(item: dict, config: dict) -> float:
    """사서 입력 컷과 카드 동점 정렬용 순위 점수.

    점수 = 휴리스틱 + 소스 가중치 + 성격 가산.
    소스 가중치(config source_weights)는 기관 원문과 사고 매체에만 준다.
    구글뉴스 대리 소스는 이름이 기관이어도 source_weights 대신
    news_proxy_weight 하나만 받는다. 성격 가산(config kind_rank_bonus)은
    사고, 법제도, 기관 발표를 올리고 단순 취약점과 무관 기사를 내린다.
    성격은 사서 판정(item kind)이 있으면 그것을, 없으면
    classify_kind_fallback 결과를 쓴다. 최종 판정은 사서가 한다."""
    if is_news_proxy(item):
        bonus = _number(config.get("news_proxy_weight", 0))
    else:
        weights = config.get("source_weights") or {}
        bonus = _number(weights.get(item.get("source", ""), 0))
    kind_bonus = config.get("kind_rank_bonus") or {}
    if kind_bonus:
        kind = item.get("kind")
        if not (isinstance(kind, str) and kind in KNOWN_KINDS):
            kind = classify_kind_fallback(item, config)
        bonus += _number(kind_bonus.get(kind, 0))
    return cardgen.heuristic_score(item) + bonus


def _cap_key(item: dict) -> str:
    # 같은 이름이라도 구글뉴스 대리 소스와 기관 원문 크롤러는 따로 센다
    # (예: 금융보안원 구글뉴스 쿼리와 fsec 게시판 크롤러)
    source = item.get("source") or ""
    return f"{source}#proxy" if is_news_proxy(item) else source


def cap_per_source(ranked: list[dict], cap: int,
                   limit: int) -> tuple[list[dict], list[dict]]:
    """순위순 목록에서 소스당 cap건까지만 골라 limit건을 채운다.

    상한 때문에 limit을 못 채우면 남은 항목을 순위순으로 더 넣는다. 사서
    슬롯을 비워 두지 않기 위해서다. 반환은 (선발, 나머지)이고 둘 다 입력
    순위 순서를 지킨다. 나머지는 이월 대상이다. cap이 0 이하면 상한 없이
    앞에서 limit건을 자른다."""
    limit = max(0, int(limit))
    if cap is None or int(cap) <= 0:
        return list(ranked[:limit]), list(ranked[limit:])
    cap = int(cap)
    counts: dict[str, int] = {}
    chosen: set[int] = set()
    for idx, item in enumerate(ranked):
        if len(chosen) >= limit:
            break
        key = _cap_key(item)
        if counts.get(key, 0) >= cap:
            continue
        counts[key] = counts.get(key, 0) + 1
        chosen.add(idx)
    for idx in range(len(ranked)):
        if len(chosen) >= limit:
            break
        chosen.add(idx)
    selected = [it for i, it in enumerate(ranked) if i in chosen]
    overflow = [it for i, it in enumerate(ranked) if i not in chosen]
    return selected, overflow


def group_same_event(ranked: list[dict]) -> tuple[list[dict], list[dict]]:
    """순위순 목록에서 같은 사건 보도를 묶어 대표 1건만 남긴다.

    판정은 dedup.is_similar_event(CVE 교집합, 제목 토큰 유사도)다. 대표는
    순위가 가장 높은 항목이다. 반환은 (대표 목록, 묶여 빠진 목록)이고 둘 다
    순위 순서를 지킨다. 빠진 항목은 버리지 않고 이월 대상으로 돌려준다."""
    reps: list[dict] = []
    grouped: list[dict] = []
    for item in ranked:
        if any(dedup_lib.is_similar_event(item, rep) for rep in reps):
            grouped.append(item)
        else:
            reps.append(item)
    return reps, grouped


def spread_sources(ranked: list[dict], config: dict,
                   decay: float) -> list[dict]:
    """같은 소스가 앞자리를 연달아 차지하지 않게 다시 줄 세운다.

    같은 소스의 k번째 항목(0부터)은 순위 점수에서 decay*k를 뺀 값으로
    정렬한다. 같은 사건을 매체마다 다른 제목으로 실은 구글뉴스 묶음(예:
    금융보안원 해킹 기사 8건)이 상위를 독식하던 문제를 누그러뜨린다.
    동점은 입력 순서를 지킨다."""
    if decay <= 0:
        return list(ranked)
    seen: dict[str, int] = {}
    keyed = []
    for idx, item in enumerate(ranked):
        key = _cap_key(item)
        k = seen.get(key, 0)
        seen[key] = k + 1
        keyed.append((-(_rank_score(item, config) - decay * k), idx, item))
    keyed.sort(key=lambda t: (t[0], t[1]))
    return [item for _, _, item in keyed]


def librarian_cut(news_ranked: list[dict],
                  config: dict) -> tuple[list[dict], list[dict]]:
    """사서 입력 뉴스 컷. news_ranked[:librarian_news_cap]을 대체한다.

    순서: 같은 사건 묶기(librarian_group_same_event, 기본 켬) 뒤 소스당
    상한(librarian_source_cap)으로 librarian_news_cap건을 고른다. 고른
    목록은 같은 소스 연속 감점(librarian_source_decay)으로 다시 줄 세운다.
    감점은 순서에만 쓰고 선발에는 쓰지 않는다. 반환은 (사서 입력 뉴스,
    이월 뉴스)다. 이월은 원래 순위 순서다."""
    limit = int(_number(config.get("librarian_news_cap", 60), 60))
    cap = int(_number(config.get("librarian_source_cap", 0), 0))
    decay = _number(config.get("librarian_source_decay", 0), 0)
    pool, grouped = list(news_ranked), []
    if config.get("librarian_group_same_event", True):
        pool, grouped = group_same_event(news_ranked)
    selected, overflow = cap_per_source(pool, cap, limit)
    selected = spread_sources(selected, config, decay)
    if grouped:
        print(f"[main] 같은 사건 묶기: {len(grouped)}건 이월", file=sys.stderr)
    rank = {id(it): i for i, it in enumerate(news_ranked)}
    overflow = sorted(overflow + grouped, key=lambda it: rank[id(it)])
    return selected, overflow


# ---------------------------------------------------------------- 규칙 분류
# 사서(LLM)가 통째로 실패한 날의 기사 성격 판정. 제목을 먼저 보고, 제목에서
# 신호가 없을 때만 요약까지 본다. 우선순위는 홍보와 칼럼(제목만), 법제도,
# 사고, 취약점, 기관 발표. 사고와 법제도와 기관 발표는 모두 뉴스 카드 성격이라
# 셋 사이 오분류는 해가 작다. 막아야 하는 것은 단순 취약점 기사와 무관 기사가
# 카드에 오르는 일이다.

def _kw_re(korean: list[str], english: list[str]) -> re.Pattern:
    # 한글은 조사가 붙으므로 부분 문자열, 영문은 단어 경계로 맞춘다.
    # 판정 텍스트를 소문자로 바꿔 넣으므로 패턴도 소문자로 둔다.
    # 두 목록 모두 정규식 조각이다(한글 쪽 lookaround 허용)
    parts = [k.lower() for k in korean]
    parts += [rf"(?<![a-z0-9]){e}(?![a-z])" for e in english]
    return re.compile("|".join(parts))


# 칼럼, 사진, 경조사, 방송 같은 비기사 표지. 제목에 있으면 무조건 other
_NON_NEWS_RE = _kw_re(
    ["\\[화촉\\]", "\\[포토\\]", "\\[기고\\]", "칼럼", "\\[인사\\]", "\\[부고\\]"],
    ["webinars?", "podcast", "stormcast"],
)
# 제품 출시, 수상, 협약, 행사 같은 홍보성 기사. 제목에만 건다. 제목에 사고
# 핵심어(_HARD_INCIDENT_RE)가 함께 있으면 홍보로 보지 않는다
_PROMO_RE = _kw_re(
    # 앞 글자 제한: "유출시"의 출시, "권한 획득" 같은 사고 문구를 피한다
    ["(?<![가-힣])출시", "(?<![가-힣])선정", "(?<![가-힣])수상(?!한)", "인증 ?획득",
     "(?<![가-힣])참가", "협약", "(?<![가-힣])체결", "(?<![가-힣])연동",
     "공모전", "(?<![가-힣])우승", "세미나", "컨퍼런스", "콘퍼런스", "인터뷰"],
    ["tips", "checklist", "awards?", "partners? with", "acquires",
     "acquisition", "raises \\$\\d+"],
)
_HARD_INCIDENT_RE = _kw_re(
    ["유출", "침해", "(?<!모의)해킹(?!대회|방어대회|\\s?대회)", "탈취"],
    ["breach(?:es|ed)?", "leak(?:s|ed)?", "stolen", "hacked"],
)
_POLICY_RE = _kw_re(
    ["개정", "법안", "법제", "시행령", "시행규칙", "시행", "입법", "국회", "의무화",
     "규제", "과징금", "과태료", "제재", "처분", "고시", "제도", "정책", "법률", "헌법",
     "징계", "소송", "판결"],
    ["laws?(?! enforcement)", "legislation", "lawmakers?", "regulations?",
     "regulators?", "regulatory", "fined", "fines?(?!-)", "penalt(?:y|ies)",
     "sanction(?:s|ed)?", "bans?", "banned", "executive order", "directive",
     "mandate[sd]?", "act", "senate", "congress", "parliament", "gdpr",
     "compliance", "sues", "sued", "lawsuit", "court"],
)
_INCIDENT_RE = _kw_re(
    ["유출", "침해", "(?<!모의)해킹(?!대회|방어대회|\\s?대회)", "피해", "탈취", "마비",
     "장애", "털렸", "털린", "뚫렸", "뚫린", "공격", "감염", "사기", "검거", "체포",
     "기소", "도용", "디도스", "손상", "분실", "노출", "공급망", "위협 그룹", "배후",
     "랜섬웨어"],
    ["breach(?:es|ed)?", "leak(?:s|ed)?", "data theft", "stolen", "stole",
     "steal(?:s|ing)?", "hacked", "hijack(?:s|ed|ing)?", "ransom\\w*",
     "cyberattacks?", "cyber[- ]attacks?", "extortion", "compromised?",
     "compromise of", "outages?", "disrupt\\w*", "defaced", "heist",
     "arrest(?:s|ed)?", "charged", "charges", "sentenced", "indicted",
     "extradited", "takedown", "seized", "exfiltrat\\w*", "victims?",
     "attack on", "attacks on", "espionage", "campaign", "supply chain",
     "threat actors?", "apt\\d*"],
)
_AGENCY_RE = _kw_re(
    ["KISA", "한국인터넷진흥원", "과기정통부", "과학기술정보통신부", "개인정보위",
     "개인정보보호위원회", "금융보안원", "금감원", "금융감독원", "금융위", "금융당국",
     "국정원", "국가정보원", "국가사이버안보센터", "경찰청", "방통위", "방송미디어통신위원회",
     "정부", "당국", "행안부", "행정안전부", "국방부", "한국은행", "보호나라"],
    ["cisa", "ncsc", "fbi", "nsa", "enisa", "europol", "nist", "interpol",
     "government", "agency", "agencies", "ministry", "department of"],
)
_ANNOUNCE_RE = _kw_re(
    ["발표", "발간", "공개", "배포", "보고서", "가이드", "안내서", "권고", "당부", "점검",
     "실태", "경고", "주의", "대응", "훈련", "지침", "출범", "착수", "결과", "방안",
     "대책", "감사", "조사"],
    ["reports?", "guides?", "guidance", "warns?", "warning", "alerts?",
     "advisory", "advisories", "publish(?:es|ed)?", "releases?", "issues?",
     "urges?", "joint", "framework", "best practices", "scheme",
     "programme", "program", "launch(?:es|ed)?"],
)
_VULN_RE = _kw_re(
    ["취약점", "패치", "보안 업데이트", "업데이트 권고", "제로데이", "원격 코드", "원격코드",
     "보안공지", "결함"],
    ["vulnerabilit(?:y|ies)", "flaws?", "patch(?:es|ed)?", "zero-day",
     "0-day", "rce", "remote code execution", "security updates?", "bugs?",
     "exploit(?:s|ed|ation)?", "cvss", "privilege escalation", "injection",
     "advisory"],
)
_CVE_ID_RE = re.compile(r"cve-\d{4}-\d{4,7}")
# 기관 이름이 제목에 없어도 국내 기관 발간물 꼴이면 기관 발표로 본다
_DOC_RE = _kw_re(["보고서", "리포트", "가이드", "매뉴얼", "안내서", "백서", "지침"], [])


def _classify_text(text: str) -> str | None:
    if not text:
        return None
    if _POLICY_RE.search(text):
        return "policy"
    if _INCIDENT_RE.search(text):
        return "incident"
    # 기관이 낸 취약점 경고도 단순 취약점 기사로 본다(사용자 결정
    # 2026-11-20: 취약점 권고는 오늘의 CVE 코너)
    if _CVE_ID_RE.search(text) or _VULN_RE.search(text):
        return "vuln"
    if _AGENCY_RE.search(text) and _ANNOUNCE_RE.search(text):
        return "institution"
    if _DOC_RE.search(text):
        return "institution"
    return None


def _is_institution_source(item: dict, config: dict | None) -> bool:
    if not config or is_news_proxy(item):
        return False
    return item.get("source") in set(config.get("institution_sources") or [])


def classify_kind_fallback(item: dict, config: dict | None = None) -> str:
    """사서 판정이 없을 때의 기사 성격. "incident", "policy", "institution",
    "vuln", "other" 중 하나를 돌려준다(KNOWN_KINDS와 같은 값).

    제목에 칼럼 같은 비기사 표지가 있거나, 사고 핵심어 없이 홍보 표지가
    있으면 other. 아니면 제목만으로 판정한다. 제목에 신호가 없을 때 기관
    원문 소스(config institution_sources) 항목은 institution, 그 밖은 제목과
    요약을 합쳐 다시 본다. 관공서 보도자료 요약은 부수 언급(취약점 등)이
    많아 요약으로 성격을 바꾸지 않는다. 취약점 권고 전용 소스
    판별(_is_vuln_source)은 호출 측이 따로 건다."""
    title = (item.get("title") or "").lower()
    if _NON_NEWS_RE.search(title):
        return "other"
    if _PROMO_RE.search(title) and not _HARD_INCIDENT_RE.search(title):
        return "other"
    kind = _classify_text(title)
    if kind is None and _is_institution_source(item, config):
        return "institution"
    if kind is None:
        summary = (item.get("summary") or "")[:600].lower()
        kind = _classify_text(f"{title} {summary}")
    return kind or "other"


def _apply_dedup_groups(items: list[dict], groups: list[list[int]]) -> list[dict]:
    """중복 게이트가 준 묶음(1-based)에서 대표 1건만 남긴 새 리스트.

    대표 선정은 카드 정렬 기준과 동일한 (-importance, -heuristic_score).
    입력 순서는 보존한다 — 정렬은 이미 끝난 뒤 호출된다."""
    drop: set[int] = set()
    for group in groups:
        winner = min(
            group,
            key=lambda n: (-(items[n - 1].get("importance") or 0),
                           -cardgen.heuristic_score(items[n - 1])),
        )
        for n in group:
            if n == winner:
                continue
            drop.add(n)
            print(
                "[main] 최종 중복 게이트 제외: "
                f"{items[n - 1].get('title_ko') or items[n - 1].get('title')} "
                f"(대표: {items[winner - 1].get('title_ko') or items[winner - 1].get('title')})",
                file=sys.stderr,
            )
    return [it for i, it in enumerate(items, start=1) if i not in drop]
