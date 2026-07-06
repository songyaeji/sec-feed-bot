"""아침 다이제스트 카드뉴스 PNG 렌더러.

templates/card.html의 조각(fragment)들을 정규식으로 추출해 {{...}}
자리표시자를 str.replace로 치환하는 방식 — 하루 1회, 카드 10장 이하라
jinja2 같은 템플릿 엔진은 과하다. 아이템 제목/요약/출처는 전부
html.escape를 거치므로 피드 본문에 섞인 마크업이 카드 레이아웃을
깨뜨리지 못한다.

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
KOREAN_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

CARD_WIDTH = 1080
CARD_HEIGHT = 1350

MAX_ISSUE_CARDS = 6
MAX_LIST_CARDS = 2      # 표지 1 + 이슈 6 + 목록 2 = 9장 (Discord 첨부 10장 한도 내)
LIST_ROWS_PER_CARD = 12
MAX_CHIP_TAGS = 3       # notify.DIGEST_MAX_TAGS와 같은 이유: 칩이 줄을 넘치지 않게

# 이슈 카드 헤더의 카테고리 한글 라벨 (미등록 카테고리는 원문 그대로 표기)
CATEGORY_LABELS = {
    "critical": "긴급",
    "high": "주요",
    "research": "리서치",
    "ai": "AI 보안",
    "news": "뉴스",
    "paper": "논문",
}
DEFAULT_ACCENT = 0x5865F2  # config colors에 없는 카테고리용 (Discord blurple)

# 표지 스탯 칩: (stats 키, 라벨, 점 색, 값 포맷). 값이 None이거나 키가
# 없으면 칩 자체를 그리지 않는다 — notify._build_header_embed와 같은
# 원칙("wiki가 안 돈 것"과 "wiki 신규 0건"은 다른 사실).
STAT_CHIP_DEFS = [
    ("total", "총", "#4A6CF7", "{}건"),
    ("urgent", "긴급", "#E74C3C", "{}"),
    ("finance", "금융", "#F1C40F", "{}"),
    ("wiki_new", "위키", "#2ECC71", "+{}"),
]

_FRAGMENT_RE = re.compile(r"<!-- BEGIN (\w+) -->\n(.*?)\n<!-- END \1 -->", re.S)


def pick_top(items: list[dict], limit: int = MAX_ISSUE_CARDS) -> list[dict]:
    """이슈 카드로 승격할 상위 아이템 선정. 가산점 방식(배타적 분기가
    아님)이라 'KEV이면서 금융' 같은 복합 이슈가 자연히 위로 올라온다.
    sorted는 안정 정렬이므로 동점은 입력 순서(=심각도 정렬 순)를 유지."""
    def score(item: dict) -> float:
        s = 0.0
        if item.get("kev"):
            s += 100
        if item.get("urgent_source"):
            s += 90
        tags = item.get("tags") or []
        if "제로데이" in tags:
            s += 80
        if "금융" in tags:
            s += 70
        if "AI" in tags:
            s += 60
        cvss = item.get("cvss")
        if cvss is not None:
            s += cvss * 5
        category = item.get("category")
        if category == "critical":
            s += 40
        elif category == "high":
            s += 20
        return s

    return sorted(items, key=score, reverse=True)[:limit]


def build_link_lines(top_items: list[dict], rest_items: list[dict]) -> list[str]:
    """카드 번호와 1:1로 매칭되는 원문 링크 목록(이슈 카드 순서 먼저).
    URL을 <>로 감싸 Discord 링크 미리보기(embed 자동 생성)를 억제한다."""
    lines = []
    for i, item in enumerate(top_items + rest_items, start=1):
        title = " ".join(item.get("title", "").split())  # 개행이 목록 줄을 깨지 않게
        lines.append(f"{i}. [{title}](<{item['url']}>)")
    return lines


def build_cards(
    items: list[dict],
    briefing: str | None = None,
    stats: dict | None = None,
    colors: dict | None = None,
) -> list[bytes]:
    """표지 1장 + 이슈 카드(pick_top 상위, 최대 6장) + 목록 카드(나머지,
    최대 2장) PNG 리스트를 돌려준다. 총 10장 이하 — Discord 웹훅 한 번에
    첨부 가능한 상한."""
    colors = colors or {}

    top = pick_top(items)
    # 동일 내용의 dict가 두 번 들어와도 안전하게 identity로 나머지를 가른다
    top_ids = {id(it) for it in top}
    rest = [it for it in items if id(it) not in top_ids]

    fragments = _load_fragments()
    shell = _load_shell()

    now_kst = datetime.now(KST)
    card_htmls = [_build_cover(fragments, now_kst, briefing, stats, n=1)]
    for i, item in enumerate(top):
        card_htmls.append(
            _build_issue(fragments, item, num=i + 1, accent=_accent(item, colors),
                         now_kst=now_kst, n=len(card_htmls) + 1)
        )
    card_htmls.extend(_build_lists(fragments, rest, colors, start_n=len(card_htmls) + 1))

    page_html = shell.replace("<!-- CARDS -->", "\n".join(card_htmls))
    return _render(page_html, card_count=len(card_htmls))


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


def _accent(item: dict, colors: dict) -> str:
    """config.yaml discord.colors의 embed 색 정수(0xE74C3C)를 CSS hex로.
    embed와 카드가 같은 카테고리 색을 쓰게 해 채널 전체 톤을 통일한다."""
    value = colors.get(item.get("category"), DEFAULT_ACCENT)
    if isinstance(value, int):
        return f"#{value:06X}"
    return str(value)


# ------------------------------------------------------------------ cards

def _build_cover(
    fragments: dict, now_kst: datetime,
    briefing: str | None, stats: dict | None, n: int,
) -> str:
    stats = stats or {}
    chips = []
    for key, label, dot, fmt in STAT_CHIP_DEFS:
        value = stats.get(key)
        if value is None:
            continue
        chips.append(_fill(fragments["stat_chip"], DOT=dot,
                           LABEL=html.escape(label), VALUE=html.escape(fmt.format(value))))

    briefing_block = ""
    if briefing:
        briefing_block = _fill(fragments["briefing"], BRIEFING=html.escape(briefing))

    weekday = KOREAN_WEEKDAYS[now_kst.weekday()]
    return _fill(
        fragments["cover"],
        N=str(n),
        DATE=f"{now_kst.month}월 {now_kst.day}일",
        WEEKDAY=f"{weekday}요일",
        BRIEFING_BLOCK=briefing_block,
        STAT_CHIPS="".join(chips),
    )


def _build_issue(
    fragments: dict, item: dict, num: int, accent: str,
    now_kst: datetime, n: int,
) -> str:
    category = item.get("category") or ""
    chips = [_fill(fragments["chip"], TEXT=html.escape(item.get("source", "")))]
    for tag in (item.get("tags") or [])[:MAX_CHIP_TAGS]:
        chips.append(_fill(fragments["chip"], TEXT=html.escape(tag)))

    badges = []
    if item.get("kev"):
        badges.append(fragments["kev_badge"])
    cvss = item.get("cvss")
    if cvss is not None:
        badges.append(_fill(fragments["cvss_tile"], CVSS=html.escape(str(cvss))))
    badge_row = _fill(fragments["badge_row"], BADGES="".join(badges)) if badges else ""

    return _fill(
        fragments["issue"],
        N=str(n),
        NUM=f"{num:02d}",
        ACCENT=accent,
        CATEGORY=html.escape(CATEGORY_LABELS.get(category, category)),
        TITLE=html.escape(item.get("title", "")),
        CHIPS="".join(chips),
        BADGES=badge_row,
        SUMMARY=html.escape(item.get("summary", "") or ""),
        FOOTER=f"보안동향 브리핑 · {now_kst.month}월 {now_kst.day}일",
    )


def _build_lists(
    fragments: dict, rest: list[dict], colors: dict, start_n: int,
) -> list[str]:
    if not rest:
        return []

    # 카드 2장 × 12행 상한. 넘치면 마지막 행 자리를 "…외 N건"으로 쓴다 —
    # 전체 목록은 어차피 링크 메시지(build_link_lines)에 전건 수록된다.
    max_rows = MAX_LIST_CARDS * LIST_ROWS_PER_CARD
    shown = rest
    more = 0
    if len(rest) > max_rows:
        shown = rest[:max_rows - 1]
        more = len(rest) - len(shown)

    cards = []
    for start in range(0, len(shown), LIST_ROWS_PER_CARD):
        chunk = shown[start:start + LIST_ROWS_PER_CARD]
        rows = [
            _fill(
                fragments["list_row"],
                DOT=_accent(item, colors),
                TITLE=html.escape(item.get("title", "")),
                SOURCE=html.escape(item.get("source", "")),
            )
            for item in chunk
        ]
        is_last = start + LIST_ROWS_PER_CARD >= len(shown)
        if more and is_last:
            rows.append(_fill(fragments["list_more"], COUNT=str(more)))
        cards.append(_fill(
            fragments["list"],
            N=str(start_n + len(cards)),
            COUNT=str(len(rest)),
            ROWS="".join(rows),
        ))
    return cards


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
            for i in range(1, card_count + 1):
                pngs.append(page.locator(f"#card-{i}").screenshot())
        finally:
            browser.close()
    return pngs
