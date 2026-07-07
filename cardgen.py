"""아침 다이제스트 카드뉴스 PNG 렌더러 — 시안 1a "네온라임 그리드" (hifi).

templates/card.html의 조각(fragment)들을 정규식으로 추출해 {{...}}
자리표시자를 str.replace로 치환하는 방식 — 하루 1회, 카드 10장 이하라
jinja2 같은 템플릿 엔진은 과하다. 아이템 제목/요약/출처는 전부
html.escape를 거치므로 피드 본문에 섞인 마크업이 카드 레이아웃을
깨뜨리지 못한다.

카드 구성(v21): 표지 1 + 뉴스(pick_top 파급력순) + 목록 1(나머지 있을 때)
+ 오늘의 CVE 1(상시) + 마무리 1(상시) = 최대 10장 (Discord 웹훅 첨부
한도 — plan_cards가 초과분을 뉴스→목록으로 강등해 강제).
v20: 텍스트 온리 — 이미지·다이어그램 슬롯 없음, 수치 pull-out이 시각 앵커.

렌더는 Playwright(chromium) 스크린샷. import는 함수 안에서 지연 —
realtime 모드(20분 cron)는 카드뉴스를 만들지 않으므로 playwright가
설치돼 있지 않아도 돌아가야 한다. 렌더 중 예외는 삼키지 않고 그대로
올린다: 호출자(main.py)가 기존 텍스트 다이제스트로 fail-open 폴백한다.
"""
import html
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "card.html")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PREVIEW_DIR = os.path.join(BASE_DIR, "state", "preview")

KST = timezone(timedelta(hours=9))
WEEKDAYS_EN = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

CARD_WIDTH = 1080
CARD_HEIGHT = 1350

MAX_ISSUE_CARDS = 7     # v21: 표지1+뉴스7+CVE1+마무리1 = 10장; 목록 있으면 plan_cards가 강등
LIST_ROWS = 10          # 목록 카드 1장의 행 상한 (넘치면 "…외 N건")
CVE_LIST_ROWS = 6       # v21: CVE 2단 행(cve_row) 높이 예산(실측 7행째 절단) — 초과분은 "…외 N건"
MAX_TAG_PILLS = 3       # 태그 pill 총 상한 — 한 줄 유지 (v19: 카테고리 pill 폐기로 한 칸 확보)

# '오늘의 CVE' 행 라벨용: 텍스트 등장 순서 기준 첫 CVE id
CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)

# 피드 제목에 섞여 오는 장식용 특수문자(딩벳·박스 등)는 번들 폰트에 글리프가
# 없어 두부(□)로 렌더된다 — ASCII 인쇄 문자 전체·한글·통용 문장부호만 남기고
# 걷어낸다 (개별 열거는 sentinel_token의 '_'처럼 정상 문자를 삼킨 전력)
_RENDERABLE_RE = re.compile(
    r"[^\x20-\x7E가-힣ㄱ-ㆎ\s·‘’“”–—…→↗]"
)


def _clean_text(text: str) -> str:
    return " ".join(_RENDERABLE_RE.sub("", text or "").split())


# 국내 피드 제목의 분류 접두어([이슈칼럼], [단독], [긴급] 등) — 카드가 이미
# 이슈를 다루는 매체라 중복 라벨(사용자 피드백 v7), 걷어낸다
_TITLE_PREFIX_RE = re.compile(r"^\s*(?:\[[^\]]{1,14}\]\s*)+")

# 사서가 summary_ko에 **키워드**로 표시한 강조 → <b class="kw">
_KW_MD_RE = re.compile(r"\*\*(.+?)\*\*")

# 피드 원문 summary 폴백용 태그 제거 — 인제스트(sources/rss.py)에서도 걷어내지만,
# 이미 마크업이 실린 채 적재된 pending 항목이 카드에 오를 수 있어 렌더에서도 방어.
# `<[^>]*$`: 인제스트가 300자 절단한 뒤라 닫는 >가 잘린 미완결 태그 꼬리도 지운다
_TAG_RE = re.compile(r"<[^>]*>|<[^>]*$")


def _strip_html(text: str) -> str:
    return " ".join(_TAG_RE.sub(" ", text or "").split())


def _card_title(item: dict) -> str:
    # v5: 카드에는 전부 한국어 — 사서 번역 제목(title_ko) 우선, 없으면 원제
    title = item.get("title_ko") or item.get("title", "")
    return _clean_text(_TITLE_PREFIX_RE.sub("", title))


def _summary_html(text: str) -> str:
    """본문 요약 → HTML. escape 후에 **키워드** 마커만 강조 태그로 바꾸므로
    피드/사서 출력에 섞인 마크업은 여전히 무력화된다. 홀수 개 ** 잔여물은
    장식이 아니라 노이즈 — 지운다."""
    escaped = html.escape(" ".join((text or "").split()))
    marked = _KW_MD_RE.sub(r'<b class="kw">\1</b>', escaped)
    return marked.replace("**", "")


# v21: 본문 문장 청크 분절용 — 청크1 = 첫 문장(핵심 사실), 청크2 = 나머지
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _summary_chunks(text: str) -> str:
    """요약을 문장 청크 <p>로 분절(v21) — 첫 문장 하나, 나머지 문장 하나.
    문장이 하나뿐이면 <p>도 하나. _summary_html 결과(escape 완료)를
    나누므로 강조 <b class="kw">는 보존되고, 태그가 문장 경계에 걸치지
    않는다는 전제는 fitAllCards와 동일하다."""
    body = _summary_html(text)
    parts = _SENT_SPLIT_RE.split(body, maxsplit=1)
    if len(parts) == 2 and parts[1].strip():
        return f"<p>{parts[0]}</p><p>{parts[1]}</p>"
    return f"<p>{body}</p>"


_FRAGMENT_RE = re.compile(r"<!-- BEGIN (\w+) -->\n(.*?)\n<!-- END \1 -->", re.S)


def heuristic_score(item: dict) -> float:
    """카드 승격용 가산점. 사서(librarian) importance의 동점 시 보조 정렬
    기준으로도 쓰인다."""
    s = 0.0
    # 사용자 = BoB AI기업보안트랙 → AI 관련 이슈를 최우선 가중.
    # KEV(100)·제로데이(80)·금융(70)보다 위로 올려 AI 항목이 카드
    # 상단을 차지하게 한다(태그는 config tags.AI: llm/prompt injection/생성형 등)
    tags = item.get("tags") or []
    if "AI" in tags:
        s += 120
    if item.get("kev"):
        s += 100
    if "제로데이" in tags:
        s += 80
    if "금융" in tags:
        s += 70
    cvss = item.get("cvss")
    if cvss is not None:
        s += cvss * 5
    category = item.get("category")
    if category == "ai":
        s += 50   # AI 보안 카테고리 소스(OWASP GenAI 등)도 가산
    elif category == "critical":
        s += 40
    elif category == "high":
        s += 20
    return s


def pick_top(items: list[dict], limit: int = MAX_ISSUE_CARDS) -> list[dict]:
    """뉴스 카드로 승격할 상위 아이템 선정. v21: 파급력(사서 importance
    1~5) 우선 정렬 — 가산점(AI·금융 등 heuristic_score)은 동점 시 보조
    기준으로 강등한다(사용자 결정: 금융 +70이 importance 5짜리 대형
    사고를 밀어내던 문제의 수정). sorted는 안정 정렬이므로 동점은 입력
    순서(=심각도 정렬 순)를 유지."""
    return sorted(
        items,
        key=lambda it: ((it.get("importance") or 0), heuristic_score(it)),
        reverse=True,
    )[:limit]


def is_cve_item(item: dict) -> bool:
    """CVE 피드 항목(KEV·NVD 등 구조적 취약점 엔트리) 여부. 기사 본문에
    CVE가 언급된 뉴스는 여기 해당하지 않는다 — kev/cvss 구조 필드로만
    판별해, NVD·KEV 덤프가 카드를 도배하는 것만 걸러낸다(사용자 v10)."""
    return bool(item.get("kev")) or item.get("cvss") is not None


def plan_cards(items: list[dict]):
    """카드 구성 순서를 한 곳에서 결정 — build_cards와 build_link_lines가
    같은 순서를 쓰게 한다. 반환: (news_top, cve_rest, other_rest).

    v15: CVE는 뉴스(보안 이슈) 카드에서 전면 제외 — v10의 '최상위 1건
    승격'도 폐기(사용자 결정). 전부 '오늘의 CVE' 코너(맨 마지막 장)로
    모으고, 표지 이슈 건수에서도 뺀다. 카드뉴스의 목적은 보안 '동향'
    추적이고 CVE 엔트리는 그 부록이다.

    v21: 총량 상한 10장(Discord 첨부 한도, preflight fatal)을 여기서
    강제 — 고정 2장(표지+CVE) + 뉴스 + 목록(있을 때 1)이 넘치면
    뉴스 최하위부터 목록 카드 맨 앞으로 강등한다. build_link_lines가
    이 반환값 순서를 그대로 쓰므로 트리밍은 반드시 여기서 끝낸다."""
    cve_items = [it for it in items if is_cve_item(it)]
    other_items = [it for it in items if not is_cve_item(it)]

    top = pick_top(other_items)
    top_ids = {id(it) for it in top}

    cve_rest = pick_top(cve_items, limit=len(cve_items))  # 중요도순 정렬만
    other_rest = [it for it in other_items if id(it) not in top_ids]
    while 2 + len(top) + (1 if other_rest else 0) > 10:
        other_rest.insert(0, top.pop())
    return top, cve_rest, other_rest


def build_link_lines(top_items: list[dict], cve_rest: list[dict],
                     other_rest: list[dict]) -> list[str]:
    """카드 번호와 1:1로 매칭되는 원문 링크 목록. 카드 표시 순서와
    동일하게 뉴스 → 그 밖의 소식 → 오늘의 CVE(맨 마지막) 순으로 나열한다.
    URL을 <>로 감싸 Discord 링크 미리보기(embed 자동 생성)를 억제한다."""
    lines = []
    for i, item in enumerate(top_items + other_rest + cve_rest, start=1):
        title = " ".join(item.get("title", "").split())  # 개행이 목록 줄을 깨지 않게
        lines.append(f"{i}. [{title}](<{item['url']}>)")
    return lines


def build_cards(
    items: list[dict],
    briefing: str | None = None,
    stats: dict | None = None,
    colors: dict | None = None,
    regions: dict[str, str] | None = None,
) -> list[bytes]:
    """표지 1 + 뉴스(pick_top 파급력순) + 목록(나머지 있을 때 1) +
    오늘의 CVE 1(상시, 항상 맨 마지막 장)의 PNG 리스트를 돌려준다.
    총 10장 이하 — Discord 웹훅 한 번에 첨부 가능한 상한과 같고,
    plan_cards가 초과분을 뉴스→목록으로 강등해 보장한다.

    colors 인자는 구 디자인(카테고리별 액센트)의 호출부 호환용으로 받되
    쓰지 않는다 — 시안 1a는 라임 단일 액센트.

    regions: 소스명 → "국내"/"해외" 맵(사용자 피드백 v7) — 뉴스 카드
    pill로 실린다. 맵에 없는 소스는 표기 생략."""
    stats = stats or {}

    # v15: 뉴스 / 그 밖의 소식 / 오늘의 CVE(맨 마지막 장) — CVE는 뉴스
    # 카드·표지 이슈 건수에서 제외(부록 코너로만)
    top, cve_rest, other_rest = plan_cards(items)
    # 표지 "N가지"는 보안 이슈(비CVE)만 센다 — main이 준 total(전체
    # to_send 건수)을 카드 표시용으로만 덮어쓴다
    stats = {**stats, "total": len(top) + len(other_rest)}

    fragments = _load_fragments()
    shell = _load_shell()

    now_kst = datetime.now(KST)
    date_full = _date_full(now_kst)     # "2026.07.06 MON"
    date_short = date_full.split(" ")[0]  # "2026.07.06"

    # 도트는 전체 장수를 먼저 알아야 그릴 수 있다(v21: 전 카드 footer):
    # 표지 1 + 뉴스 + (그 외 있을 때 1) + 오늘의 CVE 1(상시)
    total = 1 + len(top) + (1 if other_rest else 0) + 1

    card_htmls = [
        _build_cover(fragments, date_full, top, briefing, stats, total, n=1)
    ]
    for item in top:
        n = len(card_htmls) + 1
        card_htmls.append(
            _build_news(fragments, item, date_short, n=n,
                        regions=regions or {},
                        dots=_dots(fragments, total, n))
        )
    if other_rest:
        n = len(card_htmls) + 1
        card_htmls.append(
            _build_list(fragments, other_rest, date_short, n=n,
                        dots=_dots(fragments, total, n))
        )
    # '오늘의 CVE'는 항상 실린다 — 0건이어도 빈 상태 카드로 발행 기간에
    # 신규 CVE가 없었음을 명시한다(사용자 피드백 v20)
    n = len(card_htmls) + 1
    if cve_rest:
        card_htmls.append(
            _build_cve_list(fragments, cve_rest, date_short, n=n,
                            dots=_dots(fragments, total, n))
        )
    else:
        card_htmls.append(_fill(fragments["cve_empty"],
                                N=str(n),
                                DATE=html.escape(date_short),
                                DOTS=_dots(fragments, total, n)))
    assert len(card_htmls) == total

    page_html = shell.replace("<!-- CARDS -->", "\n".join(card_htmls))
    return _render(page_html, card_count=total)


# ---------------------------------------------------------------- template

def _load_shell() -> str:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        raw = f.read()
    # </html> 이후의 fragment 정의부는 페이지 본문이 아니므로 잘라낸다
    return raw.split("</html>", 1)[0] + "</html>"


def _load_fragments() -> dict[str, str]:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        raw = f.read()
    fragments = dict(_FRAGMENT_RE.findall(raw))
    if not fragments:
        raise RuntimeError(f"card.html에서 fragment를 찾지 못함: {TEMPLATE_PATH}")
    return fragments


def _fill(fragment: str, **values: str) -> str:
    for key, value in values.items():
        fragment = fragment.replace("{{" + key + "}}", value)
    return fragment


def _date_full(now_kst: datetime) -> str:
    return (
        f"{now_kst.year}.{now_kst.month:02d}.{now_kst.day:02d} "
        f"{WEEKDAYS_EN[now_kst.weekday()]}"
    )


def _dots(fragments: dict, total: int, active: int) -> str:
    """진행 도트 행 — active(1-기준) 위치만 라임 활성.
    v21: 표지 전용이던 도트를 모든 카드 footer로 확장."""
    return "".join(
        fragments["dot_active"] if i == active else fragments["dot"]
        for i in range(1, total + 1)
    )


# ------------------------------------------------------------------ cards

def _build_cover(
    fragments: dict, date_full: str, top: list[dict],
    briefing: str | None, stats: dict, total: int, n: int,
) -> str:
    # 헤드라인의 "N가지"는 다이제스트 전체 건수 — stats.total이 정본이고
    # (목록 카드에 못 실린 초과분 포함) 없으면 뉴스 카드 수로 폴백
    count = stats.get("total") or len(top)

    # v21: 표지 티저 — 상단 공백(리뷰 지적)에 파급력 1위(첫 뉴스 카드)
    # 제목 한 줄
    teaser_block = ""
    if top:
        teaser_block = _fill(fragments["cover_teaser"],
                             TITLE=html.escape(_card_title(top[0])))

    # v7: 표지 줄글(briefing) 폐기 — 해시태그가 그날의 요약을 겸한다.
    # briefing 인자는 호출부 호환용으로만 남는다.
    # v21: 해시태그는 카드 등장 순서 기반 — 뉴스 카드 각각의 첫 태그를
    # 순서대로 dedupe(리뷰: stats keywords가 카드 순서·주제를 못 덮음).
    # top이 비면 기존 stats keywords 폴백, 그래도 없으면 행 자체를 생략
    tags_block = ""
    keywords: list[str] = []
    for it in top:
        tag = (it.get("tags") or [None])[0]
        if tag and tag not in keywords:
            keywords.append(tag)
    keywords = keywords[:5]
    if not keywords:
        keywords = [k for k in (stats.get("keywords") or []) if k][:5]
    if keywords:
        tags = "".join(
            _fill(fragments["cover_tag"], TEXT=html.escape(_clean_text(k).replace(" ", "")))
            for k in keywords
        )
        tags_block = _fill(fragments["cover_tags"], TAGS=tags)

    issue_no = stats.get("issue_no")
    # 회차 카운터가 아직 없으면(구 state 등) 좌측 슬롯을 비워 우아하게 생략
    issue_label = f"NO. {issue_no}" if issue_no is not None else ""

    # v7: 헤드라인 날짜는 숫자 표기("2026.07.07") — date_full에서 요일만 뗀다
    date_head = date_full.split(" ")[0]

    return _fill(
        fragments["cover"],
        N=str(n),
        # 표지도 요일 없이 숫자 표기 — 모든 카드 헤더와 동일(사용자 피드백 v20)
        DATE_FULL=html.escape(date_full.split(" ")[0]),
        DATE_HEAD=html.escape(date_head),
        COUNT=str(count),
        TEASER_BLOCK=teaser_block,
        TAGS_BLOCK=tags_block,
        ISSUE_NO=html.escape(issue_label),
        DOTS=_dots(fragments, total, n),
    )


def _build_news(
    fragments: dict, item: dict, date_short: str, n: int,
    regions: dict[str, str], dots: str,
) -> str:
    # v19: 카테고리 라벨("주요"/"뉴스" 등) 폐기 — 분류어는 내용이 없다는
    # 사용자 피드백. 실제 키워드(tags)가 pill의 주인이 되고, 첫 태그가
    # 카테고리 pill의 라임 스타일(pill_cat)을 물려받아 시각 앵커가 된다.
    # 개수는 유동 — 태그 없으면 국내/해외·실악용만 남아도 그대로 둔다.
    pills = []
    tags = list(item.get("tags") or [])[:MAX_TAG_PILLS]
    if tags:
        pills.append(_fill(fragments["pill_cat"], TEXT=html.escape(tags[0])))
    # v7: 국내/해외 표기 — 태그와 같은 아웃라인 pill
    region = regions.get(item.get("source", ""))
    if region:
        pills.append(_fill(fragments["pill_tag"], TEXT=html.escape(region)))
    # v8: KEV(실악용 확인)만 — "긴급" 라벨은 즉시 발송 채널 전용
    if item.get("kev"):
        pills.append(fragments["pill_urgent"])
    for tag in tags[1:]:
        pills.append(_fill(fragments["pill_tag"], TEXT=html.escape(tag)))

    # v20: 텍스트 온리 — 비주얼 슬롯 폐기(사용자 결정: 이미지·diagram 없이
    # 타이포만). 본문 아래 핵심 수치 pull-out이 매거진식 시각 앵커를 대신한다.
    # v21: pull-out 실패 시 WHY 블록(사서 why_ko)이 하단 슬롯을 물려받는다
    # — 리뷰 반려된 하단 공백·밀도 편차 해소
    bottom = ""
    po = _extract_pullout(item.get("summary_ko") or "")
    if po:
        bottom = _fill(fragments["pullout"],
                       NUM=html.escape(po[0]), CAP=html.escape(po[1]))
    elif item.get("why_ko"):
        bottom = _fill(fragments["why"], TEXT=html.escape(
            " ".join(item["why_ko"].replace("**", "").split())))

    # v21: 용어 각주 — 사서 term_ko 있을 때만 한 줄
    term = ""
    if item.get("term_ko"):
        term = _fill(fragments["term"], TEXT=html.escape(
            " ".join(item["term_ko"].split())))

    return _fill(
        fragments["news"],
        N=str(n),
        DATE=html.escape(date_short),
        PILLS="".join(pills),
        TITLE=html.escape(_card_title(item)),
        TITLE_LINES="lines-3",
        BOTTOM=bottom,
        TERM=term,
        # 카드뉴스의 메인은 요약 — 사서(librarian)가 만든 한국어 요약
        # summary_ko가 있으면 우선, 없으면(사서 실패 fail-open) 피드 원문 요약.
        # v7: **키워드** 마커를 라임 강조로 변환. v21: 문장 청크 <p> 분절
        SUMMARY=_summary_chunks(item.get("summary_ko")
                                or _strip_html(item.get("summary", ""))),
        SOURCE=html.escape(item.get("source", "")),
        DOTS=dots,
    )


_PULLOUT_RE = re.compile(
    r"(\d[\d,.]*\s*(?:만\s?명|만\s?달러|억\s?원|억\s?달러|만\s?건|%|명|달러|건))")

def _extract_pullout(summary: str) -> tuple[str, str] | None:
    """본문에서 핵심 수치 1개를 뽑아 (수치구, 뒤따르는 문장 잔여부)로.
    매거진식 pull-out: 수치는 대형 라임, 잔여부("를 요구" 등)는 캡션으로
    이어 읽힌다. 어색한 캡션이 나올 바엔 생략 — 잔여부가 없거나 24자를
    넘으면 None(카드에는 여백만 남는다, fail-open)."""
    text = summary.replace("**", "")
    m = _PULLOUT_RE.search(text)
    if not m:
        return None
    # v21: 수치구에 바로 붙은 조사까지 어절 끝으로 흡수("100만 달러를") —
    # 캡션이 "를 받아냈다"처럼 조사로 시작해 어색하던 문제 수정
    end = m.end()
    while end < len(text) and not text[end].isspace():
        end += 1
    num = text[m.start():end].rstrip(".,!?·—-")
    rest = text[end:]
    # 수치가 속한 문장의 잔여부만 — 다음 문장 침범 금지
    rest = re.split(r"[.!?]", rest, maxsplit=1)[0].strip().rstrip(",·—-")
    if not (2 <= len(rest) <= 24):
        return None
    return num, rest


def _list_card(fragments: dict, heading: str, rest: list[dict],
               rows_fn, date_short: str, n: int, dots: str,
               foot: str, subhead: str = "") -> str:
    """목록 카드 공통 조립 — 헤딩과 행 생성 함수만 갈아끼운다.
    행 상한을 넘치면 마지막 행 자리를 "…외 N건"으로 쓴다 — 전체 목록은
    어차피 링크 메시지(build_link_lines)에 전건 수록된다."""
    shown = rest
    more = 0
    if len(rest) > LIST_ROWS:
        shown = rest[:LIST_ROWS - 1]
        more = len(rest) - len(shown)

    rows = [rows_fn(item) for item in shown]
    if more:
        rows.append(_fill(fragments["list_more"], COUNT=str(more)))

    return _fill(
        fragments["list"],
        N=str(n),
        HEADING=html.escape(heading),
        DATE=html.escape(date_short),
        COUNT=str(len(rest)),
        SUBHEAD=subhead,
        ROWS="".join(rows),
        FOOT=html.escape(foot),
        DOTS=dots,
        ARROW="→",
    )


def _build_list(fragments: dict, rest: list[dict], date_short: str, n: int,
                dots: str) -> str:
    def row(item: dict) -> str:
        return _fill(
            fragments["list_row"],
            TITLE=html.escape(_card_title(item)),
            SOURCE=html.escape(item.get("source", "")),
        )
    return _list_card(fragments, "그 밖의 소식", rest, row, date_short, n,
                      dots, foot="원문 링크는 아래 메시지에")


def _build_cve_list(fragments: dict, rest: list[dict], date_short: str, n: int,
                    dots: str) -> str:
    """'오늘의 CVE' 카드 — CVE 항목 전부를 한 장에 모은다(v15: 뉴스 승격
    폐지). v21: 2단 행(cve_row)으로 재작성 — 1행 = CVE 번호 + CVSS 점수
    (없으면 "—"), 2행 = 한국어 설명 전문(fit 스크립트가 폰트 축소). 행
    상한 8(2단 행 높이 예산), 초과분은 "…외 N건". 같은 제품 일괄 공개
    (제목 "제품명 — 설명" 접두가 80% 이상 동일)면 서브헤드로 묶고 행의
    중복 접두를 걷어내 잘림을 막는다."""
    titles = [_card_title(it) for it in rest]

    prefix = ""
    counts: dict[str, int] = {}
    for t in titles:
        if " — " in t:
            head = t.split(" — ", 1)[0]
            counts[head] = counts.get(head, 0) + 1
    if counts:
        head, cnt = max(counts.items(), key=lambda kv: kv[1])
        if cnt >= 0.8 * len(rest):
            prefix = head
    subhead = ""
    if prefix:
        subhead = _fill(fragments["list_subhead"],
                        TEXT=html.escape(f"{prefix} 취약점 일괄 공개"))

    shown = rest
    shown_titles = titles
    more = 0
    if len(rest) > CVE_LIST_ROWS:
        shown = rest[:CVE_LIST_ROWS]
        shown_titles = titles[:CVE_LIST_ROWS]
        more = len(rest) - CVE_LIST_ROWS

    rows = []
    for item, title in zip(shown, shown_titles):
        text = f"{item.get('id', '')} {item.get('title', '')} {item.get('summary', '')}"
        m = CVE_RE.search(text)
        cve = m.group(0).upper() if m else ""
        cvss = item.get("cvss")
        score = f"{float(cvss):.1f}" if cvss is not None else "—"
        desc = title
        if prefix:
            desc = desc.removeprefix(prefix + " — ")
        rows.append(_fill(
            fragments["cve_row"],
            ID=html.escape(cve),
            SCORE=html.escape(score),
            DESC=html.escape(desc),
        ))
    if more:
        rows.append(_fill(fragments["list_more"], COUNT=str(more)))

    return _fill(
        fragments["list"],
        N=str(n),
        HEADING=html.escape("오늘의 CVE"),
        DATE=html.escape(date_short),
        COUNT=str(len(rest)),
        SUBHEAD=subhead,
        ROWS="".join(rows),
        FOOT=html.escape("출처: NVD · 원문 링크는 아래 메시지에"),
        DOTS=dots,
        # CVE 목록은 항상 맨 마지막 장 — 다음 장 화살표 대신 종결 표기
        ARROW="end.",
    )


# ----------------------------------------------------------------- render

def _render(page_html: str, card_count: int) -> list[bytes]:
    # 지연 import: realtime 모드는 카드를 만들지 않으므로 playwright
    # 미설치 환경에서도 이 모듈 import 자체는 실패하면 안 된다
    from playwright.sync_api import sync_playwright

    # 템플릿의 ../assets/ 상대경로는 templates/ 기준이라, 조립본을
    # state/preview/에 쓰면 깨진다 → 절대 file:// URL로 치환해 어디에
    # 임시파일을 두든 폰트가 로드되게 한다
    assets_url = Path(ASSETS_DIR).as_uri()
    page_html = page_html.replace("../assets/", assets_url + "/")

    os.makedirs(PREVIEW_DIR, exist_ok=True)
    render_path = os.path.join(PREVIEW_DIR, "_render.html")
    with open(render_path, "w", encoding="utf-8") as f:
        f.write(page_html)

    pngs = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            # device_scale_factor=2: 1080px 카드를 2160px로 렌더 —
            # 모바일 디스코드에서 확대해도 텍스트가 뭉개지지 않는다
            page = browser.new_page(
                viewport={"width": CARD_WIDTH, "height": CARD_HEIGHT},
                device_scale_factor=2,
            )
            # set_content는 base URL이 없어 상대경로를 못 푼다 → file:// goto
            page.goto(Path(render_path).as_uri())
            # 폰트 로드 전에 찍으면 fallback 글꼴로 렌더된 스크린샷이 나온다
            page.evaluate("() => document.fonts.ready")
            # v17: fitAllCards의 이미지 비율 분기(naturalWidth)가 로드 완료를
            # 전제한다 — 실패 이미지는 무시(비율 분기만 생략됨)
            page.evaluate(
                "() => Promise.all(Array.from(document.images,"
                " im => im.decode().catch(() => {})))")
            # v6: 말줄임 금지 — 제목 폰트 축소·본문 문장 경계 절단 (템플릿 <script>)
            page.evaluate("() => fitAllCards()")
            for i in range(1, card_count + 1):
                pngs.append(page.locator(f"#card-{i}").screenshot())
        finally:
            browser.close()
    return pngs
