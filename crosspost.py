"""인스타그램/쓰레드 크로스포스트 — digest 발행 후처리 CLI.

Instagram Graph API는 이미지를 '공개 URL + JPEG'로만 받는다(바이너리
업로드 불가, PNG 미지원) — 디스코드 첨부(PNG·만료 쿼리 URL)는 부적합해서,
포트폴리오(github.io)에 함께 게시된 JPEG 사본(main._publish_trend가 생성,
collect.yml이 push)을 소스로 쓴다. Pages 배포가 끝나야 URL이 살아나므로
첫 카드 URL을 폴링한 뒤 발행한다. Threads는 같은 URL을 재사용한다.

계약: 어떤 실패든 exit 0 (fail-open) — 크로스포스트는 부가 기능이라
아침 발행 파이프라인(디스코드·포트폴리오)을 절대 깨면 안 된다.
토큰은 어떤 경로로도 로그에 찍지 않는다(_mask가 예외 문자열까지 방어).

수동 실행: 러너의 out/trend/meta.json 기준으로 동작하므로 digest 직후
같은 job 안에서만 의미가 있다(collect.yml의 Crosspost 스텝).
"""
import json
import os
import re
import sys
import time

import requests
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
META_PATH = os.path.join(BASE_DIR, "out", "trend", "meta.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

GRAPH_BASE = "https://graph.facebook.com/v23.0"
THREADS_BASE = "https://graph.threads.net/v1.0"

# Pages 배포 대기 — 실측 30초~3분, 여유 5분. 초과 시 이번 회차는 포기(fail-open)
PAGES_WAIT_SECONDS = 300
PAGES_POLL_INTERVAL = 15

# 미디어 컨테이너 처리 대기 — 이미지 컨테이너는 보통 수 초 내 FINISHED
CONTAINER_WAIT_SECONDS = 120
CONTAINER_POLL_INTERVAL = 4

THREADS_TEXT_MAX = 500   # Threads 본문 상한
IG_CAPTION_MAX = 2200    # Instagram 캡션 상한

_TOKEN_RE = re.compile(r"access_token=[^&\s\"']+")


def _mask(text) -> str:
    return _TOKEN_RE.sub("access_token=***", str(text))


def _api(method: str, url: str, params: dict) -> dict:
    """Graph/Threads API 호출. 실패 시 토큰 마스킹된 RuntimeError.
    오류 본문은 error.message만 남긴다(요청 파라미터 에코 방지)."""
    try:
        resp = requests.request(method, url, params=params, timeout=30)
    except requests.RequestException as exc:
        raise RuntimeError(f"API 요청 실패 ({type(exc).__name__})") from None
    try:
        body = resp.json()
    except ValueError:
        body = {}
    if not resp.ok or (isinstance(body, dict) and body.get("error")):
        msg = ""
        if isinstance(body, dict):
            msg = (body.get("error") or {}).get("message", "")
        raise RuntimeError(f"API {resp.status_code}: {_mask(msg)[:200]}")
    return body if isinstance(body, dict) else {}


def _wait_container(status_url: str, token: str, field: str) -> None:
    """미디어 컨테이너가 FINISHED가 될 때까지 폴링. ERROR/시간초과는 예외."""
    deadline = time.monotonic() + CONTAINER_WAIT_SECONDS
    while True:
        body = _api("GET", status_url, {"fields": field, "access_token": token})
        status = body.get(field)
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"컨테이너 처리 실패 (status={status})")
        if time.monotonic() > deadline:
            raise RuntimeError(f"컨테이너 처리 대기 초과 (마지막 status={status})")
        time.sleep(CONTAINER_POLL_INTERVAL)


def post_instagram(user_id: str, token: str, image_urls: list[str], caption: str) -> str:
    """IG 이미지/캐러셀 발행 → 게시물 id. 캐러셀은 2~10장 제약."""
    base = f"{GRAPH_BASE}/{user_id}"
    urls = image_urls[:10]
    if len(urls) == 1:
        container = _api("POST", f"{base}/media", {
            "image_url": urls[0], "caption": caption, "access_token": token,
        })["id"]
    else:
        children = []
        for u in urls:
            child = _api("POST", f"{base}/media", {
                "image_url": u, "is_carousel_item": "true", "access_token": token,
            })["id"]
            _wait_container(f"{GRAPH_BASE}/{child}", token, "status_code")
            children.append(child)
        container = _api("POST", f"{base}/media", {
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption,
            "access_token": token,
        })["id"]
    _wait_container(f"{GRAPH_BASE}/{container}", token, "status_code")
    published = _api("POST", f"{base}/media_publish", {
        "creation_id": container, "access_token": token,
    })
    return published.get("id", "")


def post_threads(user_id: str, token: str, image_urls: list[str], text: str) -> str:
    """Threads 이미지/캐러셀 발행 → 게시물 id."""
    base = f"{THREADS_BASE}/{user_id}"
    urls = image_urls[:10]
    text = text[:THREADS_TEXT_MAX]
    if len(urls) == 1:
        container = _api("POST", f"{base}/threads", {
            "media_type": "IMAGE", "image_url": urls[0],
            "text": text, "access_token": token,
        })["id"]
    else:
        children = []
        for u in urls:
            child = _api("POST", f"{base}/threads", {
                "media_type": "IMAGE", "image_url": u,
                "is_carousel_item": "true", "access_token": token,
            })["id"]
            _wait_container(f"{THREADS_BASE}/{child}", token, "status")
            children.append(child)
        container = _api("POST", f"{base}/threads", {
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "text": text,
            "access_token": token,
        })["id"]
    _wait_container(f"{THREADS_BASE}/{container}", token, "status")
    published = _api("POST", f"{base}/threads_publish", {
        "creation_id": container, "access_token": token,
    })
    return published.get("id", "")


def build_caption(meta: dict, hashtags: list[str]) -> str:
    """표지와 같은 재료(회차·브리핑·키워드)로 캡션 구성."""
    lines = [f"🔐 보안동향 카드뉴스 NO.{meta.get('issue_no')} | {meta.get('date')}"]
    briefing = (meta.get("briefing") or "").strip()
    if briefing:
        lines += ["", briefing]
    tags = [t for t in (meta.get("keywords") or []) if t] + list(hashtags or [])
    if tags:
        lines += ["", " ".join(f"#{t}" for t in dict.fromkeys(tags))]
    return "\n".join(lines)[:IG_CAPTION_MAX]


def wait_for_pages(url: str) -> bool:
    """github.io 배포 완료 폴링 — 첫 카드 JPEG이 200이면 전체가 같은
    커밋으로 배포된 것이다."""
    deadline = time.monotonic() + PAGES_WAIT_SECONDS
    while time.monotonic() < deadline:
        try:
            if requests.get(url, timeout=15).status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(PAGES_POLL_INTERVAL)
    return False


def main() -> int:
    if not os.path.exists(META_PATH):
        print("[crosspost] out/trend/meta.json 없음(발행 안 됨) — 스킵")
        return 0
    with open(META_PATH, encoding="utf-8") as f:
        meta = json.load(f)
    jpgs = meta.get("cards_jpg") or []
    if not jpgs:
        print("[crosspost] JPEG 카드 없음(변환 실패?) — 스킵", file=sys.stderr)
        return 0

    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = (yaml.safe_load(f) or {}).get("crosspost", {}) or {}
    except OSError:
        cfg = {}
    site_base = (cfg.get("site_base") or "").rstrip("/")
    if not site_base:
        print("[crosspost] config crosspost.site_base 미설정 — 스킵", file=sys.stderr)
        return 0

    date = meta.get("date", "")
    image_urls = [f"{site_base}/{date}/{name}" for name in jpgs]

    ig_enabled = (cfg.get("instagram") or {}).get("enabled") and \
        os.environ.get("IG_USER_ID") and os.environ.get("IG_ACCESS_TOKEN")
    th_enabled = (cfg.get("threads") or {}).get("enabled") and \
        os.environ.get("THREADS_USER_ID") and os.environ.get("THREADS_ACCESS_TOKEN")
    if not ig_enabled and not th_enabled:
        print("[crosspost] 활성 플랫폼 없음(secret 미등록 또는 disabled) — 스킵")
        return 0

    if not wait_for_pages(image_urls[0]):
        print(
            f"[crosspost] Pages 배포 대기 {PAGES_WAIT_SECONDS}s 초과 — 이번 회차 스킵",
            file=sys.stderr,
        )
        return 0

    caption = build_caption(meta, cfg.get("hashtags") or [])

    # 플랫폼별 격리 — 한쪽 실패가 다른 쪽을 막지 않는다
    if ig_enabled:
        try:
            media_id = post_instagram(
                os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"],
                image_urls, caption)
            print(f"[crosspost] Instagram 발행 완료 (media={media_id}, {len(image_urls)}장)")
        except Exception as exc:
            print(f"[crosspost] Instagram 실패(무시): {_mask(exc)}", file=sys.stderr)
    if th_enabled:
        try:
            media_id = post_threads(
                os.environ["THREADS_USER_ID"], os.environ["THREADS_ACCESS_TOKEN"],
                image_urls, caption)
            print(f"[crosspost] Threads 발행 완료 (media={media_id}, {len(image_urls)}장)")
        except Exception as exc:
            print(f"[crosspost] Threads 실패(무시): {_mask(exc)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
