"""merge_state 단위 테스트 — union 뒤 TTL 재적용(2026-08-18 회귀 방지).

main.py가 prune한 결과를 이 스크립트가 remote의 prune 전 사본과 합치므로,
union만 하면 만료 항목이 매 run 부활한다(실측: recent_titles TTL 7일인데
44일치 24,994건 잔존). 여기서 고정하는 계약 세 가지:
① remote에만 있는 만료 항목은 merge 결과에서 사라진다.
② 신선한 항목은 양쪽 어디에 있든 살아남는다.
③ 입력 dict은 변형되지 않는다(immutability).
"""
from datetime import datetime, timedelta, timezone

import dedup
import merge_state
from common import SEEN_TTL_DAYS

_NOW = datetime.now(timezone.utc)


def _iso(days_ago: float) -> str:
    return (_NOW - timedelta(days=days_ago)).isoformat()


def _state(seen_days, cve_days, title_days) -> dict:
    return {
        "seen": {f"id-{d}": _iso(d) for d in seen_days},
        "alerted_cves": {f"CVE-2026-{1000 + int(d)}": _iso(d) for d in cve_days},
        "recent_titles": [{"t": f"title {d}", "d": _iso(d)} for d in title_days],
    }


def test_expired_remote_entries_do_not_resurrect():
    # local = main.py가 막 prune한 상태(신선분만), remote = prune 전 사본
    local = _state([1], [1], [1])
    remote = _state(
        [1, SEEN_TTL_DAYS + 1],
        [1, dedup.ALERTED_CVE_TTL_DAYS + 1],
        [1, dedup.RECENT_TITLE_TTL_DAYS + 1],
    )

    merged = merge_state.merge_seen(local, remote)

    assert set(merged["seen"]) == {"id-1"}
    assert set(merged["alerted_cves"]) == {"CVE-2026-1001"}
    assert [e["t"] for e in merged["recent_titles"]] == ["title 1"]


def test_fresh_entries_from_both_sides_survive():
    local = _state([2], [2], [2])
    remote = _state([3], [3], [3])

    merged = merge_state.merge_seen(local, remote)

    assert set(merged["seen"]) == {"id-2", "id-3"}
    assert set(merged["alerted_cves"]) == {"CVE-2026-1002", "CVE-2026-1003"}
    assert {e["t"] for e in merged["recent_titles"]} == {"title 2", "title 3"}


def test_guard_dates_and_last_run_still_merge():
    local = dict(_state([1], [1], [1]), last_run=_iso(0),
                 last_digest_date="2026-08-18", last_trend_date="2026-08-17")
    remote = dict(_state([1], [1], [1]), last_run=_iso(1),
                  last_digest_date="2026-08-17", last_trend_date="2026-08-18")

    merged = merge_state.merge_seen(local, remote)

    assert merged["last_run"] == local["last_run"]      # 최신이 이긴다
    assert merged["last_digest_date"] == "2026-08-18"
    assert merged["last_trend_date"] == "2026-08-18"


def test_inputs_not_mutated():
    local = _state([1], [1], [1])
    remote = _state([1, SEEN_TTL_DAYS + 1], [1], [1])
    remote_seen_before = dict(remote["seen"])

    merge_state.merge_seen(local, remote)

    assert remote["seen"] == remote_seen_before
