"""Discord webhook delivery.

Never log the webhook URL itself (including inside exception messages)
since it's a bearer credential — anyone with it can post as the bot.

Layout: critical/high items are severe/rare enough to deserve their own
card (one glance = one incident). Everything else (news/research/ai/paper)
is high-volume and low-urgency, so those get folded into one digest embed
per category instead of flooding the channel with an embed per item.

main.py's hybrid realtime/digest mode decides urgency itself (v8:
judge.select_urgent(), major-incident LLM judgment) rather than relying
on category, so send_cards() and
send_digest() below route purely on the list they're given -- call
send_cards() with urgent items and send_digest() with everything else,
regardless of category. send()/_build_embeds() are kept for callers that
want the old category-based split in one call.
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

BATCH_SIZE = 10

WEBHOOK_USERNAME = "보안동향 브리핑"

# 피드 제목/요약은 신뢰할 수 없는 입력 — content에 @everyone/@here가
# 섞여 들어오면 채널 전체가 핑된다. 모든 멘션 파싱을 끈다
NO_MENTIONS = {"parse": []}

KST = timezone(timedelta(hours=9))
KOREAN_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]
HEADER_COLOR = 0x5865F2

# Discord embed description supports `#`/`##` headers and `-#` subtext (both
# are the same markdown parser as regular messages -- embed *title* fields
# do not get this treatment, which is why v3 moved headers/dates out of
# title and into description everywhere below). If this ever renders as
# literal "#"/"-#" characters in a client, flip this to False to fall back
# to bold+emoji / italic instead of touching every call site.
USE_HEADER_MD = True

INDIVIDUAL_SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟡",
}

# urgent (judge.select_urgent 판정) 개별 카드 강화 스타일 — 빨강 고정 색.
# urgent_reason이 있는 항목에만 적용된다.
URGENT_COLOR = 0xE74C3C

# digest bullet-line emoji, checked in priority order (first tag match wins);
# an item with no matching tag falls back to a plain bullet
DIGEST_TAG_EMOJI = [
    ("제로데이", "⚡"),
    ("금융", "💰"),
    ("AI", "🤖"),
]

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

DIGEST_MAX_LINES = 8  # was 15; each entry is now 2 lines + a blank, so fewer fit
DIGEST_TITLE_MAX = 70
DIGEST_MAX_TAGS = 3
EMBED_DESCRIPTION_MAX = 4096


def _h1(text: str) -> str:
    return f"# {text}" if USE_HEADER_MD else f"**{text}**"


def _h2(text: str) -> str:
    return f"## {text}" if USE_HEADER_MD else f"**{text}**"


def _sub(text: str) -> str:
    return f"-# {text}" if USE_HEADER_MD else f"*{text}*"


def _chip_line(source: str, tags: list[str]) -> str:
    """`-#`/italic subtext line: source name, then up to 3 tags as backtick
    chips. Shared by individual cards and digest entries so the two layouts
    read the same way."""
    line = source
    if tags:
        line += " · " + " ".join(f"`{t}`" for t in tags[:DIGEST_MAX_TAGS])
    return _sub(line)


def send(items: list[dict], discord_cfg: dict) -> None:
    """Send a mixed list of items, routing individual-card vs. digest by
    category (see DIGEST_LABELS). Kept for callers that want everything in
    one call; main.py's hybrid mode calls send_cards()/send_digest()
    directly instead so it can route by urgency rather than category."""
    colors = discord_cfg.get("colors", {})
    _dispatch(_build_embeds(items, colors))


def send_cards(items: list[dict], discord_cfg: dict) -> None:
    """Send every item as its own individual card, regardless of category.
    Used for urgent items (v8: judge.select_urgent major-incident verdicts)
    in the hybrid realtime/digest flow."""
    if not items:
        return
    colors = discord_cfg.get("colors", {})
    embeds = [_build_individual_embed(item, colors) for item in items]
    _dispatch(embeds)


def send_digest(
    items: list[dict],
    discord_cfg: dict,
    briefing: str | None = None,
    stats: dict | None = None,
) -> None:
    """Group every item into one digest embed per category, regardless of
    which categories normally get an individual card. Used for the
    non-urgent backlog (this run's non-urgent items + pending.json) in
    digest mode.

    A header embed (see _build_header_embed) is prepended in front of the
    per-category embeds carrying the librarian's briefing text (if any)
    and a run-stats line built from `stats` (total/urgent/finance/wiki_new
    -- any missing key is simply omitted from the line)."""
    if not items:
        return
    colors = discord_cfg.get("colors", {})
    digest_groups: dict[str, list[dict]] = {}
    for item in items:
        digest_groups.setdefault(item.get("category"), []).append(item)

    embeds = [_build_header_embed(briefing, stats)]
    embeds.extend(
        _build_digest_embed(category, group_items, colors)
        for category, group_items in digest_groups.items()
    )
    _dispatch(embeds)


MESSAGE_CONTENT_MAX = 2000  # Discord 일반 메시지 content 상한


def send_card_news(pngs: list[bytes], link_lines: list[str]) -> list[str]:
    """digest 카드뉴스: PNG 첨부 메시지 1건 + 원문 링크 메시지(들).

    이미지는 웹훅 multipart 업로드(files[0..9] + payload_json)로 한
    메시지에 몰아넣는다 — 한 메시지여야 모바일에서 갤러리로 묶여
    카드뉴스처럼 스와이프된다. 링크는 이미지에 넣을 수 없으니 직후
    별도 content 메시지로 보내되, 카드 번호와 줄 번호가 1:1로 맞는다
    (cardgen.build_link_lines가 그 순서를 보장).

    반환: 디스코드가 확정한 첨부 CDN URL 목록 — 크로스포스트(인스타/
    쓰레드)가 공개 URL로 재사용한다. `?wait=true`로 메시지 생성을 확정
    응답으로 받아 첨부 누락(발송 불완전)을 발송 시점에 감지한다."""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not set")

    cdn_urls: list[str] = []
    if pngs:
        files = {
            f"files[{i}]": (f"card_{i:02d}.png", png, "image/png")
            for i, png in enumerate(pngs)
        }
        resp = _post_multipart_with_retry(
            webhook_url, files,
            {"payload_json": json.dumps(
                {"username": WEBHOOK_USERNAME, "allowed_mentions": NO_MENTIONS})},
            params={"wait": "true"},
        )
        attachments = None
        try:
            attachments = resp.json().get("attachments") or []
            cdn_urls = [a.get("url", "") for a in attachments if a.get("url")]
        except ValueError:
            pass  # wait=true 미지원/이상 응답 — 2xx였으므로 발송은 된 것
        if attachments is not None and len(attachments) != len(pngs):
            if not attachments:
                # 메시지에 이미지가 하나도 안 붙었다 — 발송 실패로 취급해
                # 호출자(main)가 텍스트 다이제스트 폴백을 태우게 한다
                raise RuntimeError(f"카드 첨부 0/{len(pngs)}장 — 카드뉴스 발송 실패")
            print(
                f"[notify] 카드 첨부 {len(attachments)}/{len(pngs)}장 — 일부 누락",
                file=sys.stderr,
            )

    if link_lines:
        time.sleep(1)  # 이미지 메시지와 같은 rate-limit 버킷을 공유하므로
        chunks = _chunk_lines(link_lines, MESSAGE_CONTENT_MAX)
        for i, chunk in enumerate(chunks):
            try:
                _post_with_retry(webhook_url, {
                    "content": chunk,
                    "username": WEBHOOK_USERNAME,
                    "allowed_mentions": NO_MENTIONS,
                })
            except RuntimeError as exc:
                # 카드(이미지)는 이미 전달됐다 — 여기서 예외를 올리면 main이
                # 텍스트 다이제스트 폴백까지 발송해 이중 발행이 된다(구현
                # 전: 링크 1건 실패 = 카드+텍스트 중복). 링크 누락은 로그만.
                print(
                    f"[notify] 링크 메시지 {i + 1}/{len(chunks)} 발송 실패(카드는 전달됨): {exc}",
                    file=sys.stderr,
                )
            if i + 1 < len(chunks):
                time.sleep(1)

    return cdn_urls


def _chunk_lines(lines: list[str], limit: int) -> list[str]:
    """줄 목록을 limit자 이하 덩어리로 묶는다. 줄 중간을 자르면 마크다운
    링크가 깨지므로 항상 줄 경계에서만 나눈다 (한 줄이 limit을 넘는
    비정상 케이스만 예외적으로 절단)."""
    chunks: list[str] = []
    current = ""
    for line in lines:
        if len(line) > limit:
            line = line[:limit]
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > limit:
            chunks.append(current)
            current = line
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def _dispatch(embeds: list[dict]) -> None:
    if not embeds:
        return
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not set")

    for i in range(0, len(embeds), BATCH_SIZE):
        batch = embeds[i:i + BATCH_SIZE]
        _post_with_retry(webhook_url, {
            "embeds": batch,
            "username": WEBHOOK_USERNAME,
            "allowed_mentions": NO_MENTIONS,
        })

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
    # urgent_reason 존재 = judge가 대형 사건으로 판정한 긴급 항목.
    # 이때만 강화 스타일(빨강·🚨·사유 blockquote·심각도 타일)을 적용하고,
    # 그 외 호출 경로(send()의 category 라우팅 등)는 기존 렌더를 유지한다.
    urgent_reason = item.get("urgent_reason")

    category = item.get("category")
    if urgent_reason:
        color = URGENT_COLOR  # 긴급은 category 색 무시 — 무조건 빨강
    else:
        color = colors.get(category, colors.get("high", 0xF1C40F))

    finance_emoji = "💰" if _has_tag(item, "금융") else ""
    if urgent_reason:
        prefix_parts = ["🚨", finance_emoji]
    else:
        sev_emoji = INDIVIDUAL_SEVERITY_EMOJI.get(item.get("severity"), "")
        prefix_parts = [sev_emoji, finance_emoji]
    prefix = " ".join(p for p in prefix_parts if p)
    title = f"{prefix} {item['title']}".strip() if prefix else item["title"]

    desc_lines = []
    if urgent_reason:
        # 사유가 첫 줄에 blockquote로 크게 보이게 — "왜 지금 봐야 하는지"
        desc_lines.append(f"> ❗ **왜 긴급:** {urgent_reason}")
    # 표시용은 사서 구체 키워드(tags_ko) 우선 — 로직 판단은 규칙 태그 유지
    desc_lines.append(_chip_line(item["source"], item.get("tags_ko") or item.get("tags") or []))

    if item.get("kev"):
        if urgent_reason:
            desc_lines.append("⚠️ **실제 악용 중** — CISA KEV 등재")
        else:
            desc_lines.append("⚠️ 실제 악용 중")

    desc_lines.append("")  # blank line before the summary body
    desc_lines.append(item.get("summary", ""))

    embed = {
        "title": title[:256],
        "url": item["url"],
        "description": "\n".join(desc_lines)[:EMBED_DESCRIPTION_MAX],
        "color": color,
        "footer": {"text": item["source"]},
        "timestamp": item["published"],
    }

    if urgent_reason:
        # author는 embed 최상단에 작게 붙는 라벨 — 채널을 훑을 때 긴급
        # 카드가 한눈에 구분되게 한다 (author.name ≤ 256자 제약, 여유 충분)
        embed["author"] = {"name": "🚨 긴급 보안 알림"}

    fields = []
    # CVSS moves out of the description body into its own field (a small
    # stat tile next to the title) instead of being one more text line
    cvss = item.get("cvss")
    if cvss is not None:
        fields.append({"name": "CVSS", "value": f"**{cvss}**", "inline": True})
    if fields:
        embed["fields"] = fields

    return embed


def _build_header_embed(briefing: str | None, stats: dict | None) -> dict:
    """Leading embed for send_digest(): a big header + a small gray dateline
    in the description (embed *title* doesn't render `#` markdown, so both
    live in description now -- see USE_HEADER_MD), the librarian's prose
    briefing (if it ran and produced one), and 🔴/💰/📚 stat tiles as inline
    fields. Any stats key that's absent is left out entirely rather than
    shown as 0, since e.g. wiki_new legitimately has no meaning when the
    librarian failed open."""
    now_kst = datetime.now(KST)
    weekday = KOREAN_WEEKDAYS[now_kst.weekday()]
    stats = stats or {}
    total = stats.get("total", 0)

    desc_lines = [
        _h1("☀️ 오늘의 보안 브리핑"),
        _sub(f"{now_kst.month}월 {now_kst.day}일 {weekday}요일 · 총 {total}건"),
    ]
    if briefing:
        desc_lines.append("")
        desc_lines.append(briefing)

    fields = []
    if stats.get("urgent") is not None:
        fields.append({"name": "🔴 긴급", "value": f"**{stats['urgent']}**", "inline": True})
    if stats.get("finance") is not None:
        fields.append({"name": "💰 금융", "value": f"**{stats['finance']}**", "inline": True})
    if stats.get("wiki_new") is not None:
        fields.append({"name": "📚 위키", "value": f"**+{stats['wiki_new']}**", "inline": True})

    embed = {
        "description": "\n".join(desc_lines)[:EMBED_DESCRIPTION_MAX],
        "color": HEADER_COLOR,
    }
    if fields:
        embed["fields"] = fields
    return embed


def _bullet_emoji(item: dict) -> str:
    tags = item.get("tags") or []
    for tag, emoji in DIGEST_TAG_EMOJI:
        if tag in tags:
            return emoji
    return "•"


def _build_digest_embed(category: str, group_items: list[dict], colors: dict) -> dict:
    # send_digest() can pass a category with no explicit label — v8부터
    # KEV/KISA(critical)도 다이제스트로 오므로 critical 라벨도 정상 경로다
    label = DIGEST_LABELS.get(category, f"🗂️ {category}")
    total = len(group_items)
    color = colors.get(category, 0x95A5A6)

    # embed title doesn't render `##` markdown, so the section header lives
    # in description too (see USE_HEADER_MD), same as the header embed
    lines = [_h2(f"{label} {total}"), ""]
    for item in group_items[:DIGEST_MAX_LINES]:
        emoji = _bullet_emoji(item)
        # 제목 속 **·대괄호는 아래 **[title](url)** 마크다운을 파손시킨다
        # (QA 2026-07-23) — 볼드 마커는 걷고 대괄호는 이스케이프
        title = item["title"].replace("**", "")
        if len(title) > DIGEST_TITLE_MAX:
            title = title[:DIGEST_TITLE_MAX] + "…"
        title = title.replace("[", "\\[").replace("]", "\\]")
        lines.append(f"{emoji} **[{title}]({item['url']})**")
        lines.append(_chip_line(item["source"], item.get("tags_ko") or item.get("tags") or []))
        lines.append("")  # blank line between items

    if total > DIGEST_MAX_LINES:
        lines.append(_sub(f"…외 {total - DIGEST_MAX_LINES}건"))
    elif lines[-1] == "":
        lines.pop()  # no dangling blank line after the last item

    description = "\n".join(lines)
    if len(description) > EMBED_DESCRIPTION_MAX:
        description = description[:EMBED_DESCRIPTION_MAX - 1] + "…"

    return {
        "description": description,
        "color": color,
    }


def _safe_post(webhook_url: str, **kwargs) -> requests.Response:
    """requests.post 래퍼. 연결·타임아웃 예외(RequestException)의 문자열에는
    requests가 요청 URL을 담기 때문에, 그대로 전파되면 웹훅 URL이 CI 로그로
    샐 수 있다. 예외를 잡아 URL 없는 메시지로 바꿔 재발생시킨다."""
    try:
        return requests.post(webhook_url, timeout=kwargs.pop("timeout", 15), **kwargs)
    except requests.RequestException as e:
        raise RuntimeError(f"Discord webhook POST failed ({type(e).__name__})") from None


RETRY_ATTEMPTS = 3


def _retrying_post(post_fn) -> requests.Response:
    """429(rate limit)·5xx(일시 장애)·네트워크 예외를 최대 RETRY_ATTEMPTS회
    재시도한다. 종전에는 429 1회 재시도뿐이라 일시 장애 한 번에 아침
    발송이 불완전해졌다. 오류 메시지에 URL/본문을 넣지 않는 원칙 유지."""
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        last = attempt == RETRY_ATTEMPTS
        try:
            resp = post_fn()
        except RuntimeError:
            if last:
                raise
            time.sleep(2 * attempt)
            continue
        if resp.status_code == 429 and not last:
            try:
                retry_after = float(resp.json().get("retry_after", 1))
            except ValueError:
                # non-JSON 429 body; fall back to a sane default rather
                # than crashing the whole run
                retry_after = 1.0
            time.sleep(retry_after)
            continue
        if resp.status_code >= 500 and not last:
            time.sleep(2 * attempt)
            continue
        if not resp.ok:
            # deliberately omit webhook_url/payload details that could leak
            # the credential or flood logs; status code is enough to debug
            raise RuntimeError(
                f"Discord webhook request failed with status {resp.status_code}")
        return resp


def _post_with_retry(webhook_url: str, payload: dict) -> requests.Response:
    return _retrying_post(
        lambda: _safe_post(webhook_url, json=payload, timeout=15))


def _post_multipart_with_retry(
    webhook_url: str, files: dict, data: dict, params: dict | None = None,
) -> requests.Response:
    """PNG는 bytes라 재시도 시 그대로 재전송 가능. 이미지 10장(수 MB)은
    json POST보다 업로드가 오래 걸리므로 타임아웃 상향."""
    return _retrying_post(
        lambda: _safe_post(
            webhook_url, files=files, data=data, params=params, timeout=60))
