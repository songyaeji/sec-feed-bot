"""금융보안원(fsec.or.kr) 게시판 크롤러.

fsec는 공식 RSS가 없고, 게시판 목록을 정적 HTML이 아니라 AJAX(JSON)로 준다.
프런트(static/assets/js/bbs/bbs.js)가 호출하는 백엔드가 그대로 열려 있어
playwright 없이 `POST /bbs/list` 한 번으로 목록을 받는다:

    POST https://www.fsec.or.kr/bbs/list
    body: {"menuNo":"<board>","pagingSearchDto":{"page":1,"pageSize":N,
                                                 "searchContents":"","searchType":""}}
    resp: {"resultCode":"00","resultMsg":"<list|card|gallery>",
           "resultData":[{bbsNo,title,regDate,regUser,contents,fileCount,...}]}

여러 게시판(발간물·인텔리전스 보고서·취약점 공개·보도자료)을 config의 boards로
받아 순회한다. 게시판별 fail-open이라 하나가 죽어도 나머지는 수집된다.
"""
import html
import re
import time
from datetime import datetime, timedelta, timezone

import requests

LIST_URL = "/bbs/list"
DETAIL_URL = "/bbs/detail?menuNo={menuNo}&bbsNo={bbsNo}"

# 봇 UA는 일부 공공사이트에서 차단 이력이 있어 브라우저 UA를 쓴다
HEADERS = {
    "User-Agent": "Mozilla/5.0 (sec-feed-bot)",
    "Content-Type": "application/json; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
}

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
# 첨부-only 게시글은 본문이 '----'·'____' 같은 구분선으로 시작한다 — 제거
_RULE_RE = re.compile(r"[-_=─–—]{3,}")


def _clean(raw_html: str) -> str:
    """게시글 contents(HTML)에서 태그를 벗기고 엔티티를 풀어 카드 본문용
    평문으로 만든다. 신규 의존성 없이 stdlib re/html만 쓴다."""
    if not raw_html:
        return ""
    text = _TAG_RE.sub(" ", raw_html)
    text = html.unescape(text)
    text = _RULE_RE.sub(" ", text)  # 장식용 구분선 런 제거
    # &nbsp; 등이 풀린 뒤 남는 연속 공백/개행을 한 칸으로 정리
    text = _WS_RE.sub(" ", text).strip()
    return text


def _to_iso(reg_date: str) -> str:
    """regDate("YYYY-MM-DD")를 자정 UTC ISO 문자열로. 파싱 실패 시 현재시각."""
    try:
        d = datetime.strptime(reg_date.strip(), "%Y-%m-%d")
        return d.replace(tzinfo=timezone.utc).isoformat()
    except (TypeError, ValueError, AttributeError):
        return datetime.now(timezone.utc).isoformat()


def _fetch_board(base_url: str, menu_no, page_size: int) -> list[dict]:
    """게시판 하나의 목록 JSON을 받아 raw item 리스트를 반환."""
    payload = {
        "menuNo": str(menu_no),
        "pagingSearchDto": {
            "page": 1,
            "pageSize": page_size,
            "searchContents": "",
            "searchType": "",
        },
    }
    resp = requests.post(
        base_url.rstrip("/") + LIST_URL,
        json=payload,
        headers=HEADERS,
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("resultCode") != "00":
        return []
    return data.get("resultData") or []


def fetch(source_cfg: dict, state: dict = None, global_cfg: dict = None) -> list[dict]:
    base_url = source_cfg.get("base_url", "https://www.fsec.or.kr")
    boards = source_cfg.get("boards", [])
    category = source_cfg.get("category", "news")
    name = source_cfg.get("name", "금융보안원")
    page_size = int(source_cfg.get("page_size", 10))
    max_age_days = int(source_cfg.get("max_age_days", 21))

    # 첫 실행 때 오래된 게시물이 한꺼번에 발송되는 백로그 홍수를 막는다.
    # 저빈도 게시판이라 평시엔 최근분만 남아 영향이 없다
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)

    items = []
    for menu_no in boards:
        raw_items = None
        for attempt in (1, 2):
            try:
                raw_items = _fetch_board(base_url, menu_no, page_size)
                break
            except Exception as exc:
                # 게시판 하나가 죽어도(네트워크·스키마 변경) 나머지는 수집.
                # 연속 POST에 커넥션이 간헐적으로 끊긴다(2026-07-12 실측:
                # 뒤쪽 보드 3개 연속 ConnectionError) — 1회 재시도 후 스킵.
                # URL은 남기되 자격증명 위험이 없어 예외 타입만 찍는다
                if attempt == 2:
                    print(f"[fsec] board {menu_no} 스킵: {type(exc).__name__}")
                else:
                    time.sleep(3)
        if raw_items is None:
            continue

        for it in raw_items:
            bbs_no = it.get("bbsNo")
            if bbs_no is None:
                continue

            published = _to_iso(it.get("regDate", ""))
            try:
                if datetime.fromisoformat(published) < cutoff:
                    continue
            except ValueError:
                pass  # 파싱 불가 날짜는 버리지 않고 통과시킨다

            title = html.unescape((it.get("title") or "").strip())
            summary = _clean(it.get("contents", ""))[:300]

            items.append({
                "id": f"fsec:{menu_no}:{bbs_no}",
                "source": name,
                "category": category,
                "title": title,
                "url": base_url.rstrip("/") + DETAIL_URL.format(menuNo=menu_no, bbsNo=bbs_no),
                "summary": summary,
                "severity": "info",
                "published": published,
            })

        # 공개 게시판이라도 연속 요청은 예의상 간격을 둔다
        time.sleep(1)

    return items
