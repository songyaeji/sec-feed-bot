"""Mastodon 인스턴스의 '화제 링크'(trends/links) — trend source.

Reddit 트렌드를 대체한다(2026-08-18). Reddit은 Actions 데이터센터 IP에서
무인증 접근이 지속 불가했고 OAuth는 앱 등록 자체가 승인제로 막혔다.
Mastodon의 trends/links는 같은 역할을 무인증으로 수행한다: 인스턴스
사용자들이 실제로 공유 중인 '외부 링크'를 공유 횟수와 함께 준다 —
커뮤니티 화제성이 이미 필터라는 트렌드 레인의 전제 그대로다.

RSS가 아니라 공식 REST라 제목·요약·발행시각·매체명이 구조화돼 온다.
링크는 레딧처럼 토론 스레드가 아니라 원문으로 바로 간다.

주의: 이 엔드포인트는 인스턴스 관리자가 공개 미리보기를 끄면 무인증
401이 된다(Mastodon 공식 문서). infosec.exchange는 2026-08-18 실측에서
200이었고, 막히면 상위(main)의 소스별 fail-open이 받아낸다.
"""
import re
import sys
from datetime import datetime, timezone

import requests

from common import _safe_exc_str

# Mastodon 공식 rate limit은 IP당 5분에 300회 — 10분 주기 1회 호출은
# 여유가 크다. UA는 출처를 밝히는 용도(차단 회피 목적의 사칭 금지)
USER_AGENT = "sec-feed-bot/1.1 (+https://github.com/songyaeji/sec-feed-bot)"

DEFAULT_LIMIT = 20
# 화제성 점수로 쓸 최근 일수 — history[0]이 오늘, [1]이 어제다.
# 하루만 보면 이제 막 뜬 링크가 과소평가되고, 일주일을 보면 어제 식은
# 링크가 계속 남는다. 이틀이 '아직 뜨거운 것'과 맞는 창
SCORE_DAYS = 2


def fetch(source_cfg: dict) -> list[dict]:
    host = source_cfg.get("host")
    if not host:
        return []
    limit = int(source_cfg.get("limit", DEFAULT_LIMIT))
    min_shares = int(source_cfg.get("min_shares", 0))
    # 보안 인스턴스라도 사용자들은 일반 뉴스를 함께 공유한다(2026-08-18
    # 실측: 상위 20건에 스라소니 야생동물·기후 기사 포함). 관심축
    # (AI·보안) 밖 링크가 트렌드 슬롯을 먹지 않게 키워드로 거른다.
    # 목록이 비어 있으면 필터하지 않는다
    patterns = _compile_keywords(source_cfg.get("keywords") or [])

    url = f"https://{host}/api/v1/trends/links?limit={limit}"
    resp = requests.get(url, timeout=20, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    links = resp.json()
    if not isinstance(links, list):
        raise RuntimeError(f"{host} trends/links 응답이 목록이 아님")

    items = []
    for link in links:
        item = _to_item(link, source_cfg, host, min_shares)
        if item and _matches(item, patterns):
            items.append(item)
    return items


def _compile_keywords(keywords: list[str]) -> list:
    """키워드를 단어 경계 정규식으로. 끝의 '*'는 접두사 매칭 허용.

    부분 문자열 매칭은 오탐이 심하다(2026-08-18 실측: "ai"가 Airtag·
    against 안에 걸려 야생동물·정치 기사가 통과했다). 기본은 단어 단위로
    맞추고, 어미가 변하는 말만 'vulnerabilit*'처럼 접두사로 쓴다."""
    compiled = []
    for raw in keywords:
        k = str(raw).strip().lower()
        if not k:
            continue
        if k.endswith("*"):
            body, tail = re.escape(k[:-1]), r"[a-z0-9-]*"
        else:
            body, tail = re.escape(k), ""
        # 앞뒤가 영숫자면 단어 내부 — CVE-2026 같은 하이픈 표기는 살린다
        compiled.append(re.compile(rf"(?<![a-z0-9]){body}{tail}(?![a-z0-9])"))
    return compiled


def _matches(item: dict, patterns: list) -> bool:
    """관심축 키워드가 제목·요약·URL 어디든 있으면 통과."""
    if not patterns:
        return True
    haystack = " ".join((
        item.get("title") or "",
        item.get("summary") or "",
        item.get("url") or "",
    )).lower()
    return any(p.search(haystack) for p in patterns)


def _to_item(link: dict, source_cfg: dict, host: str,
             min_shares: int) -> dict | None:
    url = (link.get("url") or "").strip()
    title = " ".join((link.get("title") or "").split())
    # 제목 없는 링크는 카드에서 식별이 안 된다 — 경계에서 드롭
    if not title or not url.startswith(("http://", "https://")):
        return None
    shares = _recent_shares(link.get("history"))
    if shares < min_shares:
        return None

    provider = " ".join((link.get("provider_name") or "").split())
    return {
        # id에 호스트를 넣어 다른 인스턴스를 추가해도 네임스페이스가 안 겹친다
        "id": f"masto-{host}-{url}",
        "source": source_cfg.get("name", host),
        "category": source_cfg.get("category", "trend"),
        "title": title,
        "url": url,
        # 요약은 매체가 제공한 og:description — 사서를 안 타는 레인이라
        # 여기서 오는 한 줄이 trend_enrich의 유일한 본문 단서다
        "summary": " ".join((link.get("description") or "").split())[:300],
        "severity": "info",
        "published": _parse_published(link.get("published_at")),
        "score": shares,
        # 화제성 표기 — '왜 핫한지'의 결정적 근거(레딧의 업보트 자리)
        "trend_note": (f"{provider} · {shares}회 공유" if provider
                       else f"{shares}회 공유"),
    }


def _recent_shares(history) -> int:
    """최근 SCORE_DAYS일 공유 횟수 합. history는 최신일이 앞."""
    if not isinstance(history, list):
        return 0
    total = 0
    for day in history[:SCORE_DAYS]:
        try:
            total += int((day or {}).get("uses") or 0)
        except (TypeError, ValueError):
            continue
    return total


def _parse_published(raw) -> str:
    """매체 발행시각. 없거나 깨지면 '지금'으로 — 정렬에서만 쓰인다."""
    if raw:
        try:
            return datetime.fromisoformat(
                str(raw).replace("Z", "+00:00")).isoformat()
        except ValueError as exc:
            print(f"[main] mastodon published_at 파싱 실패: {_safe_exc_str(exc)}",
                  file=sys.stderr)
    return datetime.now(timezone.utc).isoformat()
