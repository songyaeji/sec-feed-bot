"""main.prune_seen 단위 테스트 — 90일 TTL·불량 타임스탬프 드롭."""
from datetime import datetime, timedelta, timezone

import main
from common import SEEN_TTL_DAYS


def test_prune_seen_ttl_and_garbage():
    now = datetime.now(timezone.utc)
    seen = {
        "fresh": now.isoformat(),
        "edge-old": (now - timedelta(days=SEEN_TTL_DAYS + 1)).isoformat(),
        "garbage": "not-a-date",
        "none-value": None,
    }
    pruned = main.prune_seen(seen)
    assert set(pruned) == {"fresh"}
    # 원본 비변경(immutability) — 호출부가 옛 dict를 계속 봐도 안전
    assert set(seen) == {"fresh", "edge-old", "garbage", "none-value"}
