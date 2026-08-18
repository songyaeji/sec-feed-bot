"""트렌드 픽 하루 1회 게이트 + 내용 우선 레이아웃 회귀 테스트.

2026-08-13 변경 두 건을 고정한다:
  ① 발송은 카드뉴스 발행 run(digest)에서 하루 1회만 — realtime run은 보류.
  ② Discord 렌더 순서는 제목 → 설명 → 링크(구: 링크 → 설명).
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import notify  # noqa: E402
import trend_lane  # noqa: E402

KST = timezone(timedelta(hours=9))
MORNING = datetime(2026, 8, 14, 7, 30, tzinfo=KST)


def test_realtime_run_never_sends():
    """10분마다 도는 realtime run은 트렌드를 절대 내보내지 않는다 —
    하루 여러 번 알림이 오던 원인(구 6시간 스로틀)의 회귀 방지."""
    assert not trend_lane._should_send_trend({}, MORNING, "realtime")


def test_digest_run_sends_once_per_day():
    state = {}
    assert trend_lane._should_send_trend(state, MORNING, "digest")
    # 발송 성공 기록 후에는 같은 날 재진입(force_digest 재발행)에도 거짓
    state["last_trend_date"] = "2026-08-14"
    assert not trend_lane._should_send_trend(state, MORNING, "digest")
    # 날이 바뀌면 다시 참
    next_day = MORNING + timedelta(days=1)
    assert trend_lane._should_send_trend(state, next_day, "digest")


def test_layout_puts_content_before_link(monkeypatch):
    """항목당 3행: 제목 / 설명 subtext / 링크. 링크가 제목보다 뒤여야 한다."""
    sent = {}
    monkeypatch.setenv("DISCORD_TREND_WEBHOOK_URL", "https://example.invalid/hook")
    monkeypatch.setattr(notify, "_post_with_retry",
                        lambda url, payload: sent.update(payload))

    notify.send_trend([{
        "title": "Claude Skills 실전 활용법",
        "url": "https://www.youtube.com/watch?v=abc",
        "kind_emoji": "🎬",
        "trend_note": "YouTube",
        "why_ko": "스킬 자동 로딩 구조를 데모로 설명",
    }], {})

    lines = sent["embeds"][0]["description"].split("\n")
    assert lines[0] == "🎬 **Claude Skills 실전 활용법**"
    assert lines[1] == "-# ↳ YouTube · 스킬 자동 로딩 구조를 데모로 설명"
    # 링크는 마지막 — 도메인 라벨, <>로 미리보기 억제, www 제거
    assert lines[2] == "[🔗 youtube.com](<https://www.youtube.com/watch?v=abc>)"


def test_untrusted_title_cannot_break_markdown(monkeypatch):
    """피드 제목은 신뢰 불가 입력 — 강조/링크 문자가 서식을 깨면 안 된다."""
    sent = {}
    monkeypatch.setenv("DISCORD_TREND_WEBHOOK_URL", "https://example.invalid/hook")
    monkeypatch.setattr(notify, "_post_with_retry",
                        lambda url, payload: sent.update(payload))

    notify.send_trend([{
        "title": "**bold** [link](evil) `code`",
        "url": "https://example.com/x",
    }], {})

    first = sent["embeds"][0]["description"].split("\n")[0]
    # 대괄호가 이스케이프돼 있으면 [text](url) 링크로 파싱되지 않는다
    assert "\\[link\\]" in first
    assert first.startswith("📄 **\\*\\*bold\\*\\*")
    assert "\\`code\\`" in first


def test_merge_state_preserves_daily_guard():
    """merge_state 화이트리스트 누락은 하루 1회 가드를 무력화한다 —
    origin과 로컬 중 늦은 날짜가 살아남아야 같은 날 중복 발송을 막는다."""
    import merge_state

    merged = merge_state.merge_seen(
        {"seen": {}, "last_trend_date": "2026-08-17"},
        {"seen": {}, "last_trend_date": "2026-08-18"},
    )
    assert merged["last_trend_date"] == "2026-08-18"
    # 구 스로틀 키는 화이트리스트 밖 — merge를 거치며 자연 소거된다
    assert "last_trend_sent" not in merge_state.merge_seen(
        {"seen": {}, "last_trend_sent": "2026-08-18T05:03:00+00:00"}, {"seen": {}})
