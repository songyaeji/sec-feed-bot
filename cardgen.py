"""아침 다이제스트 카드뉴스 PNG 렌더러 — 시안 1a "네온라임 그리드" (hifi).

templates/card.html의 조각(fragment)들을 정규식으로 추출해 {{...}}
자리표시자를 str.replace로 치환하는 방식 — 하루 1회, 카드 10장 이하라
jinja2 같은 템플릿 엔진은 과하다. 아이템 제목/요약/출처는 전부
html.escape를 거치므로 피드 본문에 섞인 마크업이 카드 레이아웃을
깨뜨리지 못한다.

카드 구성(v5): 표지 1 + 뉴스(pick_top 중요도순, 최대 8) + 목록 1(나머지
있을 때) = 최대 10장 (Discord 웹훅 첨부 한도와 동일).
뉴스 카드 이미지는 기사 og:image가 있을 때만 그린다 — 없으면 슬롯 생략.

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

MAX_ISSUE_CARDS = 7     # v6: 표지 1 + 뉴스 7 + 목록 1 = 9장
LIST_ROWS = 10          # 목록 카드 1장의 행 상한 (넘치면 "…외 N건")
MAX_TAG_PILLS = 2       # 카테고리·긴급 pill 외 태그 pill 상한 — 한 줄 유지

# 기사 og:image 다운로드 상한 — 렌더 한 번에 8장이라 과한 대기 금지
IMG_TIMEOUT = 8
IMG_MAX_BYTES = 8 * 1024 * 1024

# v9 품질 게이트: 슬롯(952×340, cover 크롭)에서 볼만한 이미지만 통과.
# 저해상도는 업스케일로 뭉개지고, 세로 사진은 크롭이 흉하다
IMG_MIN_WIDTH = 600
IMG_MIN_HEIGHT = 315
IMG_MIN_ASPECT = 1.0   # 세로(portrait) 이미지 배제
OG_IMAGE_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\']og:image(?::url)?["\'][^>]+content=["\']([^"\']+)["\']'
    r'|<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image(?::url)?["\']',
    re.IGNORECASE,
)

# 뉴스 카드 카테고리 pill의 한글 라벨 (미등록 카테고리는 원문 그대로 표기)
# v8: "긴급"은 즉시 발송(judge 판정)의 전유 라벨 — 다이제스트 카드의
# critical 카테고리는 "중대"로 표기해 채널 의미와 충돌하지 않게 한다
CATEGORY_LABELS = {
    "critical": "중대",
    "high": "주요",
    "research": "리서치",
    "ai": "AI 보안",
    "news": "뉴스",
    "paper": "논문",
}

# 이미지 슬롯 중앙 라벨용: 텍스트 등장 순서 기준 첫 CVE id
CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)

# 피드 제목에 섞여 오는 장식용 특수문자(딩벳·박스 등)는 번들 폰트에 글리프가
# 없어 두부(□)로 렌더된다 — 한글·라틴·숫자·통용 문장부호만 남기고 걷어낸다
_RENDERABLE_RE = re.compile(
    r"[^0-9A-Za-z가-힣ㄱ-ㆎ\s.,·‘’“”'\"()\[\]%:;!?~&+/\-–—…→↗]"
)


def _clean_text(text: str) -> str:
    return " ".join(_RENDERABLE_RE.sub("", text or "").split())


# 국내 피드 제목의 분류 접두어([이슈칼럼], [단독], [긴급] 등) — 카드가 이미
# 이슈를 다루는 매체라 중복 라벨(사용자 피드백 v7), 걷어낸다
_TITLE_PREFIX_RE = re.compile(r"^\s*(?:\[[^\]]{1,14}\]\s*)+")

# 사서가 summary_ko에 **키워드**로 표시한 강조 → <b class="kw">
_KW_MD_RE = re.compile(r"\*\*(.+?)\*\*")


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
    """뉴스 카드로 승격할 상위 아이템 선정. 가산점 방식(배타적 분기가
    아님)이라 'KEV이면서 금융' 같은 복합 이슈가 자연히 위로 올라온다.
    sorted는 안정 정렬이므로 동점은 입력 순서(=심각도 정렬 순)를 유지."""
    return sorted(items, key=heuristic_score, reverse=True)[:limit]


def _is_cve_item(item: dict) -> bool:
    """CVE 피드 항목(KEV·NVD 등 구조적 취약점 엔트리) 여부. 기사 본문에
    CVE가 언급된 뉴스는 여기 해당하지 않는다 — kev/cvss 구조 필드로만
    판별해, NVD·KEV 덤프가 카드를 도배하는 것만 걸러낸다(사용자 v10)."""
    return bool(item.get("kev")) or item.get("cvss") is not None


def plan_cards(items: list[dict]):
    """카드 구성 순서를 한 곳에서 결정 — build_cards와 build_link_lines가
    같은 순서를 쓰게 한다. 반환: (news_top, cve_rest, other_rest).

    v10: CVE는 가장 중요한 1건만 뉴스 카드로 승격하고, 나머지 CVE는
    별도 '오늘의 CVE' 목록으로 뺀다(사용자 결정). 일반 뉴스의 초과분은
    기존 '그 밖의 소식' 목록으로 간다."""
    cve_items = [it for it in items if _is_cve_item(it)]
    other_items = [it for it in items if not _is_cve_item(it)]

    promoted = pick_top(cve_items, limit=1)   # 최상위 CVE 1건만 뉴스 후보
    news_pool = other_items + promoted
    top = pick_top(news_pool)
    top_ids = {id(it) for it in top}

    # CVE 목록은 중요도순으로, 뉴스로 승격된 1건을 뺀 나머지
    cve_rest = [it for it in pick_top(cve_items, limit=len(cve_items))
                if id(it) not in top_ids]
    other_rest = [it for it in other_items if id(it) not in top_ids]
    return top, cve_rest, other_rest


def build_link_lines(top_items: list[dict], cve_rest: list[dict],
                     other_rest: list[dict]) -> list[str]:
    """카드 번호와 1:1로 매칭되는 원문 링크 목록. 카드 표시 순서와
    동일하게 뉴스 → 오늘의 CVE → 그 밖의 소식 순으로 나열한다.
    URL을 <>로 감싸 Discord 링크 미리보기(embed 자동 생성)를 억제한다."""
    lines = []
    for i, item in enumerate(top_items + cve_rest + other_rest, start=1):
        title = " ".join(item.get("title", "").split())  # 개행이 목록 줄을 깨지 않게
        lines.append(f"{i}. [{title}](<{item['url']}>)")
    return lines


def build_cards(
    items: list[dict],
    briefing: str | None = None,
    stats: dict | None = None,
    colors: dict | None = None,
    image_sources: set[str] | None = None,
    regions: dict[str, str] | None = None,
) -> list[bytes]:
    """표지 1장 + 뉴스 카드(pick_top 중요도순, 최대 8장) + 목록 카드(나머지
    있을 때 1장)의 PNG 리스트를 돌려준다. 총 10장 이하 — Discord 웹훅
    한 번에 첨부 가능한 상한과 같다.

    colors 인자는 구 디자인(카테고리별 액센트)의 호출부 호환용으로 받되
    쓰지 않는다 — 시안 1a는 라임 단일 액센트.

    image_sources: 기사 og:image를 카드에 실을 소스명 집합. 국내 매체의
    og:image는 대부분 스톡 일러스트라 정보가 없고(사용자 피드백 v6),
    THN·Unit42류는 공격 체인 다이어그램이 실려 유의미 — 소스 단위로
    가른다. None이면 이미지 전면 생략.

    regions: 소스명 → "국내"/"해외" 맵(사용자 피드백 v7) — 뉴스 카드
    pill로 실린다. 맵에 없는 소스는 표기 생략."""
    stats = stats or {}

    # v10: 뉴스(CVE 1건 포함) / 오늘의 CVE / 그 밖의 소식으로 분리
    top, cve_rest, other_rest = plan_cards(items)

    fragments = _load_fragments()
    shell = _load_shell()

    now_kst = datetime.now(KST)
    date_full = _date_full(now_kst)     # "2026.07.06 MON"
    date_short = date_full.split(" ")[0]  # "2026.07.06"

    # 표지 도트는 전체 장수를 먼저 알아야 그릴 수 있다:
    # v10 구성 = 표지 1 + 뉴스 + (오늘의 CVE 있을 때 1) + (그 외 있을 때 1)
    total = 1 + len(top) + (1 if cve_rest else 0) + (1 if other_rest else 0)

    card_htmls = [
        _build_cover(fragments, date_full, items, briefing, stats, total, n=1)
    ]
    for item in top:
        card_htmls.append(
            _build_news(fragments, item, date_short, n=len(card_htmls) + 1,
                        image_sources=image_sources or set(),
                        regions=regions or {})
        )
    if cve_rest:
        card_htmls.append(
            _build_cve_list(fragments, cve_rest, date_short, n=len(card_htmls) + 1)
        )
    if other_rest:
        card_htmls.append(
            _build_list(fragments, other_rest, date_short, n=len(card_htmls) + 1)
        )
    assert len(card_htmls) == total

    # 페이지 표기("02 / 08")는 전체 장수를 알아야 채울 수 있어
    # 카드 조립이 끝난 뒤 2차 치환으로 채운다 (표지에는 {{PAGE}} 없음)
    card_htmls = [
        h.replace("{{PAGE}}", f"{i:02d} / {total:02d}")
        for i, h in enumerate(card_htmls, start=1)
    ]

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


def _fetch_article_image(item: dict, slot_index: int) -> str | None:
    """기사 페이지의 og:image를 내려받아 로컬 파일 경로를 돌려준다.
    v5: 이미지는 '기사 안의 그림'이 있을 때만 그린다 — og:image가 없거나
    다운로드가 실패하면 None을 돌려주고 카드는 슬롯 없이 본문을 늘린다.
    렌더 실패로 이어지면 안 되므로 모든 예외는 None으로 흡수(fail-open)."""
    import requests  # 지연 import: cardgen import 자체는 의존성 없이 가능해야 함

    url = item.get("url")
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=IMG_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
        if not resp.ok:
            return None
        m = OG_IMAGE_RE.search(resp.text)
        if not m:
            return None
        img_url = html.unescape(m.group(1) or m.group(2))

        img = requests.get(img_url, timeout=IMG_TIMEOUT, stream=True,
                           headers={"User-Agent": "Mozilla/5.0"})
        if not img.ok or "image" not in img.headers.get("Content-Type", ""):
            return None
        data = img.raw.read(IMG_MAX_BYTES + 1)
        if not data or len(data) > IMG_MAX_BYTES:
            return None
        if not _image_quality_ok(data):
            return None

        os.makedirs(PREVIEW_DIR, exist_ok=True)
        path = os.path.join(PREVIEW_DIR, f"_img_{slot_index:02d}")
        with open(path, "wb") as f:
            f.write(data)
        return path
    except Exception:
        return None


def _image_quality_ok(data: bytes) -> bool:
    """v9 게이트: 저해상도/세로 이미지는 슬롯에서 뭉개지거나 흉하게
    크롭되므로 탈락시킨다 (탈락 시 인포패널 또는 본문 확장으로 대체).
    Pillow가 없거나 판독 실패면 통과 — 게이트는 개선이지 의존성이 아니다."""
    try:
        import io
        from PIL import Image
        with Image.open(io.BytesIO(data)) as im:
            w, h = im.size
        return (
            w >= IMG_MIN_WIDTH
            and h >= IMG_MIN_HEIGHT
            and w / h >= IMG_MIN_ASPECT
        )
    except Exception:
        return True


# ------------------------------------------------------------------ cards

def _build_cover(
    fragments: dict, date_full: str, items: list[dict],
    briefing: str | None, stats: dict, total: int, n: int,
) -> str:
    # 헤드라인의 "N가지"는 다이제스트 전체 건수 — stats.total이 정본이고
    # (목록 카드에 못 실린 초과분 포함) 없으면 아이템 수로 폴백
    count = stats.get("total") or len(items)

    # v7: 표지 줄글(briefing) 폐기 — 해시태그가 그날의 요약을 겸한다.
    # briefing 인자는 호출부 호환용으로만 남는다.
    # 키워드 해시태그 행 — 사서가 뽑은 keywords(stats 경유),
    # 없으면 표지에서 행 자체를 생략
    tags_block = ""
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

    dots = fragments["dot_active"] + fragments["dot"] * (total - 1)

    # v7: 헤드라인 날짜는 숫자 표기("2026.07.07") — date_full에서 요일만 뗀다
    date_head = date_full.split(" ")[0]

    return _fill(
        fragments["cover"],
        N=str(n),
        DATE_FULL=html.escape(date_full),
        DATE_HEAD=html.escape(date_head),
        COUNT=str(count),
        TAGS_BLOCK=tags_block,
        ISSUE_NO=html.escape(issue_label),
        DOTS=dots,
    )


def _build_news(
    fragments: dict, item: dict, date_short: str, n: int,
    image_sources: set[str], regions: dict[str, str],
) -> str:
    category = item.get("category") or ""
    cat_label = CATEGORY_LABELS.get(category, category)

    pills = []
    if cat_label:
        pills.append(_fill(fragments["pill_cat"], TEXT=html.escape(cat_label)))
    # v7: 국내/해외 표기 — 카테고리 바로 옆, 태그와 같은 아웃라인 pill
    region = regions.get(item.get("source", ""))
    if region:
        pills.append(_fill(fragments["pill_tag"], TEXT=html.escape(region)))
    # v8: KEV(실악용 확인)만 아웃라인 pill — "긴급" 라벨은 즉시 발송
    # 채널 전용이 됐으므로 사실 그대로 "실악용"으로 표기
    if item.get("kev"):
        pills.append(fragments["pill_urgent"])
    for tag in (item.get("tags") or [])[:MAX_TAG_PILLS]:
        pills.append(_fill(fragments["pill_tag"], TEXT=html.escape(tag)))

    # v5: 기사 og:image가 실제로 있을 때만 이미지 슬롯을 그린다.
    # 없으면 슬롯을 통째로 생략하고 본문 클램프를 4줄→7줄로 늘린다
    # v6: 이미지는 유의미한 소스(image_sources)만. 세로 예산상 이미지
    # 카드는 제목 2줄, 없으면 3줄 — 넘치는 본문은 fit 스크립트가 문장
    # 경계로 줄여 '…' 없이 끝맺는다
    # v9: 이미지 우선순위 — ① 소스 이미지(품질 게이트 통과 시)
    # ② CVE/CVSS 인포패널(우리가 그리는 타이포 비주얼 — 렌더라 AI 티 없음)
    # ③ 둘 다 없으면 슬롯 생략, 본문이 공간 사용
    img_path = None
    if item.get("source") in image_sources:
        img_path = _fetch_article_image(item, slot_index=n)
    if img_path:
        img_block = _fill(fragments["img_photo"], SRC=Path(img_path).as_uri())
        title_lines = "lines-2"
    else:
        img_block = _build_info_panel(fragments, item)
        title_lines = "lines-2" if img_block else "lines-3"
    return _fill(
        fragments["news"],
        N=str(n),
        DATE=html.escape(date_short),
        PILLS="".join(pills),
        TITLE=html.escape(_card_title(item)),
        IMG_BLOCK=img_block,
        TITLE_LINES=title_lines,
        # 카드뉴스의 메인은 요약 — 사서(librarian)가 만든 한국어 요약
        # summary_ko가 있으면 우선, 없으면(사서 실패 fail-open) 피드 원문 요약.
        # v7: **키워드** 마커를 라임 강조로 변환
        SUMMARY=_summary_html(item.get("summary_ko") or item.get("summary", "") or ""),
        SOURCE=html.escape(item.get("source", "")),
    )


def _build_info_panel(fragments: dict, item: dict) -> str:
    """CVE가 있는 항목의 이미지 대체 비주얼 — CVE id + CVSS 게이지.
    데이터가 없으면 빈 문자열(패널 없이 본문 확장). 억지로 채우는
    장식은 가독성에 기여하지 않는다(사용자 v9 기준)."""
    text = f"{item.get('id', '')} {item.get('title', '')} {item.get('summary', '')}"
    m = CVE_RE.search(text)
    if not m:
        return ""
    cve = m.group(0).upper()

    right = ""
    cvss = item.get("cvss")
    if cvss is not None:
        pct = max(0, min(100, int(float(cvss) * 10)))
        right = _fill(
            fragments["info_panel_score"],
            SCORE=f"{float(cvss):.1f}",
            PCT=str(pct),
        )
    return _fill(fragments["info_panel"], CVE=html.escape(cve), RIGHT=right)


def _list_card(fragments: dict, heading: str, rest: list[dict],
               rows_fn, date_short: str, n: int) -> str:
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
        ROWS="".join(rows),
    )


def _build_list(fragments: dict, rest: list[dict], date_short: str, n: int) -> str:
    def row(item: dict) -> str:
        return _fill(
            fragments["list_row"],
            TITLE=html.escape(_card_title(item)),
            SOURCE=html.escape(item.get("source", "")),
        )
    return _list_card(fragments, "그 밖의 소식", rest, row, date_short, n)


def _build_cve_list(fragments: dict, rest: list[dict], date_short: str, n: int) -> str:
    """v10 '오늘의 CVE' 카드 — 뉴스로 승격되지 않은 CVE 항목을 한 장에
    모은다. 행 제목은 'CVE-번호 · 한국어 제목', 우측은 CVSS 점수(없으면
    실악용 표기). CVE 번호는 원문 유지(사용자 결정)."""
    def row(item: dict) -> str:
        text = f"{item.get('id', '')} {item.get('title', '')} {item.get('summary', '')}"
        m = CVE_RE.search(text)
        cve = m.group(0).upper() if m else ""
        title = _card_title(item)
        label = f"{cve} · {title}" if cve else title

        cvss = item.get("cvss")
        if cvss is not None:
            source = f"CVSS {float(cvss):.1f}"
        elif item.get("kev"):
            source = "실악용"
        else:
            source = item.get("source", "")
        return _fill(
            fragments["list_row"],
            TITLE=html.escape(label),
            SOURCE=html.escape(source),
        )
    return _list_card(fragments, "오늘의 CVE", rest, row, date_short, n)


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
            # v6: 말줄임 금지 — 제목 폰트 축소·본문 문장 경계 절단 (템플릿 <script>)
            page.evaluate("() => fitAllCards()")
            for i in range(1, card_count + 1):
                pngs.append(page.locator(f"#card-{i}").screenshot())
        finally:
            browser.close()
    return pngs
