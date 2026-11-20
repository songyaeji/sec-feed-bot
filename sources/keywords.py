"""소스 크롤러 공용 키워드 필터.

한글 키워드는 조사가 붙어 쓰이므로 부분 문자열로, 영문 키워드는 단어
경계로 맞춘다("ai"가 email, said에 걸리지 않게). 대소문자는 무시한다.
"""
import re

_ASCII_RE = re.compile(r"^[\x00-\x7f]+$")


def _matches(keyword: str, text: str) -> bool:
    kw = keyword.lower()
    if _ASCII_RE.match(kw):
        return re.search(rf"(?<![a-z0-9]){re.escape(kw)}(?![a-z0-9])", text) is not None
    return kw in text


def match_any(text: str, keywords: list[str]) -> bool:
    haystack = (text or "").lower()
    return any(_matches(k, haystack) for k in keywords if k)
