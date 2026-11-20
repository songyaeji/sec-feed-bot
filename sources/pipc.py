"""개인정보보호위원회(pipc.go.kr) 보도자료 게시판 크롤러.

공식 RSS가 없다(rss 경로 404, 2026-11-20 실측). 보도자료 목록은 표준
eGovFrame 게시판이라 GET 한 번에 정적 HTML로 온다(1쪽 10건):

    <td class="boardTitle">
        <a href="/np/cop/bbs/selectBoardArticle.do?bbsId=BS074&mCode=C020010000&nttId=12660">
            제목 <span class="new">N</span></a></td>
    <td>작성부서</td>
    <td>2026-11-18</td>

목록에는 본문이 없다. 상세 페이지 td.tbl_cnts에 보도자료 앞부분이 있어
처음 보는 항목만 상세를 받아 summary로 쓴다. 이미 본 항목(state seen)과
신선도 밖 항목은 상세를 받지 않는다. 사이트 부담을 줄이려고 run당 상세
요청 수를 detail_limit으로 묶고 요청 사이에 간격을 둔다.
"""
import html
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urlparse

import requests

from sources.keywords import match_any

UA = "sec-feed-bot/1.0"
TIMEOUT = 20
DEFAULT_URL = ("https://pipc.go.kr/np/cop/bbs/selectBoardList.do"
               "?bbsId=BS074&mCode=C020010000")
# 상세 요청 사이 간격(초). 테스트는 0으로 덮어쓴다
DETAIL_INTERVAL = 1.0

_ROW_RE = re.compile(
    r'<a href="(/np/cop/bbs/selectBoardArticle\.do\?[^"]*?nttId=(\d+)[^"]*)">'
    r'(.*?)</a>\s*</td>\s*<td>[^<]*</td>\s*<td>\s*(\d{4}-\d{2}-\d{2})\s*</td>',
    re.S,
)
_NEW_BADGE_RE = re.compile(r'<span class="new">.*?</span>', re.S)
_TAG_RE = re.compile(r"<[^>]*>")
_BODY_RE = re.compile(r'<td[^>]*class="tbl_cnts"[^>]*>(.*?)</td>', re.S)
_BBS_RE = re.compile(r"bbsId=([A-Za-z0-9]+)")


def _text(fragment: str) -> str:
    text = _TAG_RE.sub(" ", fragment or "")
    return " ".join(html.unescape(text).split())


def _to_iso(date_str: str) -> str:
    try:
        d = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return d.replace(tzinfo=timezone.utc).isoformat()
    except (TypeError, ValueError):
        return datetime.now(timezone.utc).isoformat()


def parse_list(page_html: str, base_url: str) -> list[dict]:
    """목록 HTML을 [{ntt, title, url, published}]로. 순서는 페이지 순서."""
    rows = []
    for href, ntt, raw_title, date in _ROW_RE.findall(page_html):
        title = _text(_NEW_BADGE_RE.sub(" ", raw_title))
        if not title:
            continue
        rows.append({
            "ntt": ntt,
            "title": title,
            # 세션 id가 붙은 링크는 쓰지 않는다. 목록 href 그대로 절대 경로화
            "url": urljoin(base_url, html.unescape(href)),
            "published": _to_iso(date),
        })
    return rows


def parse_detail(page_html: str) -> str:
    """상세 HTML의 본문 칸(td.tbl_cnts) 텍스트. 없으면 빈 문자열."""
    m = _BODY_RE.search(page_html or "")
    if not m:
        return ""
    text = _text(m.group(1))
    # 보도자료 본문 끝의 첨부 안내 꼬리
    return text.replace("※ 이하 전문 참조", "").strip()


def _get(url: str) -> requests.Response:
    resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA})
    resp.raise_for_status()
    return resp


def fetch(source_cfg: dict, state: dict = None, global_cfg: dict = None) -> list[dict]:
    url = source_cfg.get("url") or DEFAULT_URL
    name = source_cfg.get("name", "개인정보보호위원회 보도자료")
    category = source_cfg.get("category", "news")
    keywords = source_cfg.get("keywords") or []
    detail_limit = int(source_cfg.get("detail_limit", 5))
    if "max_age_days" in source_cfg:
        max_age_days = source_cfg["max_age_days"]
    else:
        max_age_days = (global_cfg or {}).get("default_max_age_days")
    cutoff = None
    if max_age_days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=int(max_age_days))
    seen = (state or {}).get("seen") or {}

    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}/"
    bbs_match = _BBS_RE.search(url)
    bbs = bbs_match.group(1) if bbs_match else "BS074"

    rows = parse_list(_get(url).text, base_url)

    items = []
    details = 0
    for row in rows:
        if cutoff is not None:
            try:
                if datetime.fromisoformat(row["published"]) < cutoff:
                    continue
            except ValueError:
                pass
        if keywords and not match_any(row["title"], keywords):
            continue
        item_id = f"pipc:{bbs}:{row['ntt']}"
        summary = ""
        if item_id not in seen and details < detail_limit:
            details += 1
            try:
                summary = parse_detail(_get(row["url"]).text)
            except requests.RequestException as exc:
                # 상세 실패는 제목만으로 싣는다(목록은 이미 받았다)
                print(f"[pipc] 상세 스킵 {row['ntt']}: {type(exc).__name__}")
            time.sleep(DETAIL_INTERVAL)
        items.append({
            "id": item_id,
            "source": name,
            "category": category,
            "title": row["title"],
            "url": row["url"],
            "summary": summary[:1500],
            "severity": "info",
            "published": row["published"],
        })
    return items
