"""GitHub 급상승 레포 (trend source) — 두 신호를 합친다.

① github.com/trending 스크래핑(주 신호): '오늘 받은 star' 기준의 진짜
   트렌딩. 공식 API가 없어 HTML 파싱이며(2026-07-24 실측: article.Box-row
   구조) 마크업 변경에 취약하므로 실패는 조용히 ②만으로 진행한다.
② 검색 API(보조): '최근 N일 내 생성 + star M개 이상' = 신규 프로젝트의
   초기 폭발(2026-07-24 실측: xai-org/grok-build 22k★/8일). trending에
   아직 안 뜬 신생 레포를 보완한다. 무인증 한도 10req/min — run당 1회.

score는 '하루당 star'로 통일해 두 신호를 한 큐에서 정렬 가능하게 한다:
trending은 stars-today 그대로, 신규 레포는 총 star/공개일수.
AI·보안 무관 레포(웹 템플릿 등)는 keywords로 배제한다.
"""
import html as html_lib
import re
import sys
from datetime import datetime, timedelta, timezone

import requests

TRENDING_URL = "https://github.com/trending?since=daily"
SEARCH_URL = "https://api.github.com/search/repositories"
DEFAULT_MAX_AGE_DAYS = 14
DEFAULT_MIN_STARS = 300
DEFAULT_LIMIT = 10
_BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

_REPO_NAME_RE = re.compile(r"^[\w.-]+/[\w.-]+$")
_TAG_RE = re.compile(r"<[^>]+>")


def fetch(source_cfg: dict) -> list[dict]:
    keywords = [k.lower() for k in source_cfg.get("keywords", [])]
    limit = int(source_cfg.get("limit", DEFAULT_LIMIT))

    items: list[dict] = []
    seen_repos: set[str] = set()
    try:
        items.extend(_fetch_trending(source_cfg, keywords, seen_repos))
    except Exception as exc:
        print(f"[github] trending 스크랩 실패(검색 API만): "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
    try:
        items.extend(_fetch_new_repos(source_cfg, keywords, seen_repos))
    except Exception as exc:
        print(f"[github] 신규 레포 검색 실패: {type(exc).__name__}: {exc}",
              file=sys.stderr)

    items.sort(key=lambda it: -(it.get("score") or 0))
    return items[:limit]


def _matches(keywords: list[str], *texts: str) -> bool:
    if not keywords:
        return True
    haystack = " ".join(t for t in texts if t).lower()
    return any(kw in haystack for kw in keywords)


def _fetch_trending(
    source_cfg: dict, keywords: list[str], seen_repos: set[str],
) -> list[dict]:
    resp = requests.get(
        TRENDING_URL, timeout=20, headers={"User-Agent": _BROWSER_UA})
    resp.raise_for_status()

    today = datetime.now(timezone.utc).date().isoformat()
    items = []
    # 레포 하나당 <article class="Box-row"> 블록 — 블록 단위로 잘라
    # 첫 레포 링크·설명·'N stars today'를 각각 뽑는다
    for block in resp.text.split('<article class="Box-row"')[1:]:
        # 레포명은 반드시 <h2> 제목 앵커에서 — 블록 첫 href는 sponsor
        # 링크일 수 있다(2026-07-24 실측: sponsors/* 오수집)
        name_m = re.search(r'<h2[^>]*>.*?href="/([^"?]+)"', block, re.S)
        if not name_m or not _REPO_NAME_RE.match(name_m.group(1)):
            continue
        full_name = name_m.group(1)
        if full_name in seen_repos:
            continue
        # 설명 p는 col-9 클래스 고정, 뒤 클래스는 변동(tmp-pr-4 실측)
        desc_m = re.search(r'<p class="col-9[^"]*">\s*(.*?)\s*</p>', block, re.S)
        description = ""
        if desc_m:
            description = html_lib.unescape(
                _TAG_RE.sub("", desc_m.group(1))).strip()
        if not _matches(keywords, full_name, description):
            continue
        stars_today_m = re.search(r"([\d,]+)\s+stars today", block)
        stars_today = (
            int(stars_today_m.group(1).replace(",", "")) if stars_today_m else 0)
        seen_repos.add(full_name)
        items.append({
            # 같은 레포가 여러 날 트렌딩에 떠도 하루 한 번만 — id에 날짜.
            # (전날 항목은 seen에 남아 있으니 재등장해도 격일 이상은 아니고,
            #  연속 트렌딩 = 실제로 계속 핫한 것이라 재알림이 맞다)
            "id": f"github-trending-{full_name}-{today}",
            "source": source_cfg.get("name", "GitHub 급상승"),
            "category": source_cfg.get("category", "trend"),
            "title": f"{full_name} — {description}" if description else full_name,
            "url": f"https://github.com/{full_name}",
            "summary": description[:500],
            "severity": "info",
            "published": datetime.now(timezone.utc).isoformat(),
            "score": stars_today,
            "trend_note": f"GitHub 오늘 ⭐+{stars_today:,}",
        })
    return items


def _fetch_new_repos(
    source_cfg: dict, keywords: list[str], seen_repos: set[str],
) -> list[dict]:
    max_age_days = int(source_cfg.get("max_age_days", DEFAULT_MAX_AGE_DAYS))
    min_stars = int(source_cfg.get("min_stars", DEFAULT_MIN_STARS))
    since = (datetime.now(timezone.utc) - timedelta(days=max_age_days)).date()

    resp = requests.get(
        SEARCH_URL,
        params={
            "q": f"created:>{since.isoformat()} stars:>{min_stars}",
            "sort": "stars",
            "order": "desc",
            "per_page": 30,
        },
        timeout=20,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "sec-feed-bot/1.0",
        },
    )
    resp.raise_for_status()

    items = []
    for repo in resp.json().get("items", []):
        full_name = repo.get("full_name") or ""
        url = repo.get("html_url") or ""
        if not full_name or full_name in seen_repos:
            continue
        if not url.startswith(("http://", "https://")):
            continue
        description = repo.get("description") or ""
        if not _matches(keywords, full_name, description,
                        " ".join(repo.get("topics") or [])):
            continue
        stars = int(repo.get("stargazers_count") or 0)
        age_days = _age_days(repo.get("created_at"))
        seen_repos.add(full_name)
        items.append({
            "id": f"github-{repo.get('id') or full_name}",
            "source": source_cfg.get("name", "GitHub 급상승"),
            "category": source_cfg.get("category", "trend"),
            "title": f"{full_name} — {description}" if description else full_name,
            "url": url,
            "summary": description[:500],
            "severity": "info",
            "published": repo.get("created_at")
                         or datetime.now(timezone.utc).isoformat(),
            # trending의 stars-today와 같은 축(하루당 star)으로 환산
            "score": stars // max(1, age_days or 1),
            "trend_note": f"GitHub ⭐{stars:,} · 공개 {max(1, age_days or 1)}일차",
        })
    return items


def _age_days(created_at) -> int | None:
    try:
        created = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return max(0, (datetime.now(timezone.utc) - created).days)
