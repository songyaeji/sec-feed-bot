"""Keyword-based tagging for feed items.

Tags are decorative metadata layered on top of category/severity: a single
item can carry multiple tags (e.g. a ransomware story about a bank is both
'금융' and '랜섬웨어'), so this does simple keyword matching against
title+summary rather than picking one bucket.

2026-11-20 QA C10: 매처는 text_rules.keyword_matcher 하나다. card_editor의
태그 근거 검사와 같은 매처라 판정이 어긋나지 않는다. 하이픈과 공백 동치,
복수형(zero-days, LLMs), 전부 대문자 키워드는 대소문자 구분(apt-get 제외),
한글 충돌어 제외(페이지, 딥페이크의 '페이')는 그 함수 설명에 있다.
"""
import text_rules


def tag_item(item: dict, rules: dict) -> dict:
    haystack = f"{item.get('title', '')} {item.get('summary', '')}"
    item["tags"] = [tag_name for tag_name, keywords in rules.items()
                    if text_rules.any_keyword(keywords, haystack)]
    return item
