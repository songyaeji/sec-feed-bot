"""Keyword-based tagging for feed items.

Tags are decorative metadata layered on top of category/severity: a single
item can carry multiple tags (e.g. a ransomware story about a bank is both
'금융' and '랜섬웨어'), so this does simple substring matching against
title+summary rather than picking one bucket.
"""


def tag_item(item: dict, rules: dict) -> dict:
    haystack = f"{item.get('title', '')} {item.get('summary', '')}".lower()

    matched = []
    for tag_name, keywords in rules.items():
        if any(kw.lower() in haystack for kw in keywords):
            matched.append(tag_name)

    item["tags"] = matched
    return item
