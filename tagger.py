"""Keyword-based tagging for feed items.

Tags are decorative metadata layered on top of category/severity: a single
item can carry multiple tags (e.g. a ransomware story about a bank is both
'금융' and '랜섬웨어'), so this does simple keyword matching against
title+summary rather than picking one bucket.

2026-11-20: 영문 키워드는 단어 경계로만 맞춘다. 구 방식은 부분 문자열이라
"rce"가 source·resource·force에, "apt"가 chapter·capture·adapt에 걸려 기사와
무관한 태그가 붙었다(사용자 보고: 태그가 기사 내용과 불일치). 한글 키워드는
조사가 붙어 쓰이므로(랜섬웨어가, 금융권) 부분 문자열 그대로 둔다.
뒤에 숫자는 허용한다 — APT29, APT41 같은 그룹명이 apt에 걸려야 한다.
"""
import re

_ASCII_RE = re.compile(r"^[\x00-\x7f]+$")


def _matcher(keyword: str):
    kw = keyword.lower()
    if _ASCII_RE.match(kw):
        pattern = re.compile(rf"(?<![a-z0-9]){re.escape(kw)}(?![a-z])")
        return lambda text: bool(pattern.search(text))
    return lambda text: kw in text


def tag_item(item: dict, rules: dict) -> dict:
    haystack = f"{item.get('title', '')} {item.get('summary', '')}".lower()

    matched = []
    for tag_name, keywords in rules.items():
        if any(_matcher(kw)(haystack) for kw in keywords):
            matched.append(tag_name)

    item["tags"] = matched
    return item
