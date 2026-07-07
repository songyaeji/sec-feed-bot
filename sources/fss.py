"""금융감독원(fss.or.kr) 게시판 크롤러.

FSS는 표준 eGovFrame 게시판이라 목록이 **정적 HTML**로 온다(AJAX·JS 불필요).
`GET /fss/bbs/{bbsId}/list.do?menuNo={menuNo}` 응답의 테이블에서 행마다
`view.do?nttId=…` 링크(제목)와 등록일이 그대로 박혀 있다:

    <td class="title"><a href="…/view.do?nttId=219088&menuNo=200218">제목</a></td>
    …<td>담당부서</td>… <td> 2026-07-07 </td>

주의: FSS WAF가 봇/HTTP2를 끊는다 — 브라우저 UA로 요청해야 200이 온다(실측).
목록에는 본문이 없어 summary는 제목만 싣는다(카드의 summary_ko는 librarian이
제목·본문 맥락으로 재작성하므로 v1은 제목으로 충분). 게시판별 fail-open.
"""
import re
import time
from datetime import datetime, timedelta, timezone

import requests

# FSS는 봇 UA/HTTP2를 WAF가 리셋 — 브라우저 UA로 위장해야 열린다
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "ko-KR,ko"}

LIST_URL = "{base}/fss/bbs/{bbs}/list.do?menuNo={menu}"
VIEW_URL = "{base}/fss/bbs/{bbs}/view.do?nttId={ntt}&menuNo={menu}"

# 한 행에서 (상세 href) (제목) …그 뒤 첫 YYYY-MM-DD(=등록일)까지. 첨부파일명의
# 260707 같은 날짜는 대시가 없어 매칭되지 않으므로 등록일만 잡힌다
_ROW_RE = re.compile(
    r'class="title"><a href="([^"]*view\.do\?nttId=\d+[^"]*)">([^<]+)</a>.*?(\d{4}-\d{2}-\d{2})',
    re.S,
)
_NTT_RE = re.compile(r"nttId=(\d+)")


def _to_iso(date_str: str) -> str:
    try:
        d = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return d.replace(tzinfo=timezone.utc).isoformat()
    except (TypeError, ValueError):
        return datetime.now(timezone.utc).isoformat()


def _get(url: str) -> requests.Response:
    """FSS WAF가 연속 요청을 간헐적으로 리셋(ConnectionError/SSLError)한다 —
    한 번 재시도한다. 재시도로도 실패하면 예외를 올려 게시판별 fail-open으로 넘긴다."""
    try:
        return requests.get(url, headers=HEADERS, timeout=20)
    except requests.RequestException:
        time.sleep(2)
        return requests.get(url, headers=HEADERS, timeout=20)


def _fetch_board(base_url: str, bbs: str, menu: str) -> list[tuple]:
    """게시판 하나의 list.do를 받아 (nttId, title, iso_date) 리스트로."""
    url = LIST_URL.format(base=base_url.rstrip("/"), bbs=bbs, menu=menu)
    resp = _get(url)
    resp.raise_for_status()
    rows = []
    for href, title, date in _ROW_RE.findall(resp.text):
        m = _NTT_RE.search(href)
        if not m:
            continue
        rows.append((m.group(1), title.strip(), _to_iso(date)))
    return rows


def fetch(source_cfg: dict, state: dict = None, global_cfg: dict = None) -> list[dict]:
    base_url = source_cfg.get("base_url", "https://www.fss.or.kr")
    boards = source_cfg.get("boards", [])
    category = source_cfg.get("category", "news")
    name = source_cfg.get("name", "금융감독원")
    max_age_days = int(source_cfg.get("max_age_days", 21))

    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)

    items = []
    for board in boards:
        bbs = str(board.get("bbs"))
        menu = str(board.get("menu"))
        try:
            rows = _fetch_board(base_url, bbs, menu)
        except Exception as exc:
            # 게시판 하나가 죽어도 나머지는 수집(자격증명 위험 없어 타입만 로깅)
            print(f"[fss] board {bbs}/{menu} 스킵: {type(exc).__name__}")
            time.sleep(1)
            continue

        # WAF가 연속 요청에 민감하다 — 게시판 사이에 간격을 둔다
        time.sleep(1)

        for ntt, title, published in rows:
            try:
                if datetime.fromisoformat(published) < cutoff:
                    continue
            except ValueError:
                pass  # 파싱 불가 날짜는 버리지 않고 통과

            items.append({
                "id": f"fss:{menu}:{ntt}",
                "source": name,
                "category": category,
                "title": title,
                "url": VIEW_URL.format(base=base_url.rstrip("/"), bbs=bbs, ntt=ntt, menu=menu),
                "summary": "",  # 목록엔 본문이 없다 — summary_ko는 librarian이 생성
                "severity": "info",
                "published": published,
            })

    return items
