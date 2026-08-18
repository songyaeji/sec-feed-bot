"""소스 수집 — FETCHERS 매핑, 소스별 fail-open 수집, id 기반 dedup."""
import os
import sys

from common import _safe_exc_str
from sources import (
    dblp, fsec, fss, github_trend, hackernews, kev, mastodon, nvd, reddit,
    rss)

FETCHERS = {
    "kev": kev.fetch,
    "nvd": nvd.fetch,
    "rss": rss.fetch,
    "fsec": fsec.fetch,
    "fss": fss.fetch,
    "dblp": dblp.fetch,
    "hn": hackernews.fetch,
    "reddit": reddit.fetch,
    "github": github_trend.fetch,
    "mastodon": mastodon.fetch,
}


def collect_all(config: dict, state: dict) -> list[dict]:
    all_items = []
    for source_cfg in config.get("sources", []):
        source_type = source_cfg.get("type")
        fetcher = FETCHERS.get(source_type)
        name = source_cfg.get("name", "<unnamed>")

        if fetcher is None:
            print(f"[main] unknown source type '{source_type}' for '{name}', skipping", file=sys.stderr)
            continue

        try:
            if source_type == "nvd":
                items = fetcher(source_cfg, state, config)
            elif source_type in ("rss", "fsec", "fss"):
                items = fetcher(source_cfg, state, config)
            else:
                items = fetcher(source_cfg)
            # v8: 소스 단위 urgent 플래그 폐기 — 즉시 발송은 judge.py
            # (대형 사건 판정)만 결정한다. breaking 소스(HN·레딧)는
            # 판정 전용: 긴급 아니면 다이제스트에도 안 싣고 버린다
            if source_cfg.get("breaking"):
                for item in items:
                    item["breaking"] = True
            # 트렌드 라운드로빈 묶음 키 — 유튜브 채널 4개가 각각 소스로
            # 잡혀 링크 섹션을 독식하는 것 방지(_select_trend가 본다)
            if source_cfg.get("trend_group"):
                for item in items:
                    item["trend_group"] = source_cfg["trend_group"]
            print(f"[main] {name}: fetched {len(items)} item(s)", file=sys.stderr)
            all_items.extend(items)
        except Exception as exc:
            # one flaky source (network blip, bad feed URL, etc.) should
            # never take down the whole run; mask potential webhook
            # tokens since some requests exceptions embed the request URL
            print(f"[main] source '{name}' failed: {_safe_exc_str(exc)}", file=sys.stderr)
    return all_items


def max_items_per_run(config: dict) -> int | None:
    # applies only to individual cards (urgent items); the digest embed
    # already caps itself at DIGEST_MAX_LINES per category ("...외 N건"),
    # so it never needs this cap. env wins over config so a workflow can
    # raise/lower the cap without a commit
    env_value = os.environ.get("MAX_ITEMS_PER_RUN")
    if env_value is not None:
        try:
            return int(env_value)
        except ValueError:
            print(f"[main] invalid MAX_ITEMS_PER_RUN '{env_value}', ignoring", file=sys.stderr)
    return config.get("max_items_per_run")


def dedup(items: list[dict], seen: dict) -> list[dict]:
    new_items = []
    for item in items:
        if item["id"] not in seen:
            new_items.append(item)
    return new_items
