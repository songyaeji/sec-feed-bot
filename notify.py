"""Discord webhook delivery.

Never log the webhook URL itself (including inside exception messages)
since it's a bearer credential — anyone with it can post as the bot.

Layout: critical/high items are severe/rare enough to deserve their own
card (one glance = one incident). Everything else (news/research/ai/paper)
is high-volume and low-urgency, so those get folded into one digest embed
per category instead of flooding the channel with an embed per item.

main.py's hybrid realtime/digest mode decides urgency itself (see
is_urgent() there) rather than relying on category, so send_cards() and
send_digest() below route purely on the list they're given -- call
send_cards() with urgent items and send_digest() with everything else,
regardless of category. send()/_build_embeds() are kept for callers that
want the old category-based split in one call.
"""
import os
import time

import requests

BATCH_SIZE = 10

INDIVIDUAL_SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟡",
}

# category -> digest embed title label. Used by send()/_build_embeds()'s
# old category-based routing (membership here means "goes to digest"), and
# by _build_digest_embed() as a label lookup for send_digest(), which can
# receive any category (e.g. a non-urgent "high" item) -- unmapped
# categories there fall back to a generic label instead of KeyError'ing.
DIGEST_LABELS = {
    "news": "📰 보안 뉴스",
    "research": "🔬 리서치",
    "ai": "🤖 AI 보안",
    "paper": "🎓 논문",
    "high": "🟡 주요 소식",
}

DIGEST_MAX_LINES = 15
DIGEST_TITLE_MAX = 80
EMBED_DESCRIPTION_MAX = 4096


def send(items: list[dict], discord_cfg: dict) -> None:
    """Send a mixed list of items, routing individual-card vs. digest by
    category (see DIGEST_LABELS). Kept for callers that want everything in
    one call; main.py's hybrid mode calls send_cards()/send_digest()
    directly instead so it can route by urgency rather than category."""
    colors = discord_cfg.get("colors", {})
    _dispatch(_build_embeds(items, colors))


def send_cards(items: list[dict], discord_cfg: dict) -> None:
    """Send every item as its own individual card, regardless of category.
    Used for urgent items (see main.is_urgent) in the hybrid realtime/digest
    flow."""
    if not items:
        return
    colors = discord_cfg.get("colors", {})
    embeds = [_build_individual_embed(item, colors) for item in items]
    _dispatch(embeds)


def send_digest(items: list[dict], discord_cfg: dict) -> None:
    """Group every item into one digest embed per category, regardless of
    which categories normally get an individual card. Used for the
    non-urgent backlog (this run's non-urgent items + pending.json) in
    digest mode."""
    if not items:
        return
    colors = discord_cfg.get("colors", {})
    digest_groups: dict[str, list[dict]] = {}
    for item in items:
        digest_groups.setdefault(item.get("category"), []).append(item)

    embeds = [
        _build_digest_embed(category, group_items, colors)
        for category, group_items in digest_groups.items()
    ]
    _dispatch(embeds)


def _dispatch(embeds: list[dict]) -> None:
    if not embeds:
        return
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not set")

    for i in range(0, len(embeds), BATCH_SIZE):
        batch = embeds[i:i + BATCH_SIZE]
        _post_with_retry(webhook_url, {"embeds": batch})

        # Discord rate-limits webhooks fairly aggressively; a fixed pause
        # between batches keeps us under the limit without needing to
        # parse the rate-limit headers on the happy path
        if i + BATCH_SIZE < len(embeds):
            time.sleep(1)


def _build_embeds(items: list[dict], colors: dict) -> list[dict]:
    embeds = []
    digest_groups: dict[str, list[dict]] = {}

    for item in items:
        category = item.get("category")
        if category in DIGEST_LABELS:
            digest_groups.setdefault(category, []).append(item)
        else:
            embeds.append(_build_individual_embed(item, colors))

    # digest embeds come after individual cards so the urgent stuff is
    # always at the top of the message
    for category, group_items in digest_groups.items():
        embeds.append(_build_digest_embed(category, group_items, colors))

    return embeds


def _has_tag(item: dict, tag: str) -> bool:
    return tag in (item.get("tags") or [])


def _build_individual_embed(item: dict, colors: dict) -> dict:
    category = item.get("category")
    color = colors.get(category, colors.get("high", 0xF1C40F))

    sev_emoji = INDIVIDUAL_SEVERITY_EMOJI.get(item.get("severity"), "")
    prefix_parts = [p for p in (sev_emoji, "💰" if _has_tag(item, "금융") else "") if p]
    prefix = " ".join(prefix_parts)
    title = f"{prefix} {item['title']}".strip() if prefix else item["title"]

    desc_lines = []
    tags = item.get("tags") or []
    if tags:
        desc_lines.append("🏷️ " + " · ".join(tags))

    cvss = item.get("cvss")
    if cvss is not None:
        desc_lines.append(f"CVSS: {cvss}")

    if item.get("kev"):
        desc_lines.append("⚠️ 실제 악용 중")

    if desc_lines:
        desc_lines.append("")  # blank line before the summary body
    desc_lines.append(item.get("summary", ""))

    return {
        "title": title[:256],
        "url": item["url"],
        "description": "\n".join(desc_lines)[:EMBED_DESCRIPTION_MAX],
        "color": color,
        "footer": {"text": item["source"]},
        "timestamp": item["published"],
    }


def _build_digest_embed(category: str, group_items: list[dict], colors: dict) -> dict:
    # send_digest() can pass a category with no explicit label (e.g. a
    # non-urgent "critical" item, which shouldn't normally occur since KEV
    # and KISA are both `urgent: true`, but this keeps it from KeyError'ing
    # if that ever changes)
    label = DIGEST_LABELS.get(category, f"🗂️ {category}")
    total = len(group_items)
    color = colors.get(category, 0x95A5A6)

    lines = []
    for item in group_items[:DIGEST_MAX_LINES]:
        money = "💰 " if _has_tag(item, "금융") else ""
        title = item["title"]
        if len(title) > DIGEST_TITLE_MAX:
            title = title[:DIGEST_TITLE_MAX] + "…"
        lines.append(f"{money}• [{title}]({item['url']})")

    if total > DIGEST_MAX_LINES:
        lines.append(f"…외 {total - DIGEST_MAX_LINES}건")

    description = "\n".join(lines)
    if len(description) > EMBED_DESCRIPTION_MAX:
        description = description[:EMBED_DESCRIPTION_MAX - 1] + "…"

    return {
        "title": f"{label} ({total}건)"[:256],
        "description": description,
        "color": color,
    }


def _post_with_retry(webhook_url: str, payload: dict) -> None:
    resp = requests.post(webhook_url, json=payload, timeout=15)

    if resp.status_code == 429:
        try:
            retry_after = resp.json().get("retry_after", 1)
        except ValueError:
            # non-JSON 429 body; fall back to a sane default rather than
            # crashing the whole run over a malformed rate-limit response
            retry_after = 1
        time.sleep(float(retry_after))
        resp = requests.post(webhook_url, json=payload, timeout=15)

    if not resp.ok:
        # deliberately omit webhook_url/payload details that could leak
        # the credential or flood logs; status code is enough to debug
        raise RuntimeError(f"Discord webhook request failed with status {resp.status_code}")
