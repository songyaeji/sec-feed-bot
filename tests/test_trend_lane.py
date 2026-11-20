"""트렌드 픽 회귀 테스트.

고정하는 것:
  ① 발송은 카드뉴스 발행 run(digest)에서 하루 1회만 — realtime run은 보류.
  ② 2026-11-20 개편: 하루 최대 2건, 한국어 제목 / 설명 / 도메인 링크,
     영어 원제 미표시, 선정 실패 시 미발송.
"""
import json
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


def _capture(monkeypatch):
    sent = {}
    monkeypatch.setenv("DISCORD_TREND_WEBHOOK_URL", "https://example.invalid/hook")
    monkeypatch.setattr(notify, "_post_with_retry",
                        lambda url, payload: sent.update(payload))
    return sent


def test_layout_is_korean_title_then_reason_then_link(monkeypatch):
    """시안 A(2026-11-20 사용자 선택): 굵은 한국어 제목 / subtext 설명 /
    도메인 링크. 영어 원제·이모지·가운뎃점 없음."""
    sent = _capture(monkeypatch)
    notify.send_trend([{
        "title": "obra/superpowers: An agentic skills framework",
        "title_ko": "에이전트 개발 방법론 프레임워크 superpowers",
        "why_ko": "GitHub에서 하루 만에 별 2천 개를 받은 스킬 묶음이다.",
        "url": "https://www.github.com/obra/superpowers",
    }], {})

    embed = sent["embeds"][0]
    assert embed["title"].startswith("트렌드 픽 ")
    lines = embed["description"].split("\n")
    assert lines[0] == "**에이전트 개발 방법론 프레임워크 superpowers**"
    assert lines[1] == "-# GitHub에서 하루 만에 별 2천 개를 받은 스킬 묶음이다."
    assert lines[2] == "[github.com](<https://www.github.com/obra/superpowers>)"
    assert "agentic" not in embed["description"]
    assert "color" not in embed


def test_item_without_korean_title_is_not_rendered(monkeypatch):
    _capture(monkeypatch)
    import pytest
    with pytest.raises(RuntimeError):
        notify.send_trend([{"title": "English only", "url": "https://e.com/x"}], {})


def test_untrusted_text_cannot_break_markdown(monkeypatch):
    """LLM 문안도 신뢰 불가 피드에서 나왔다 — 강조/링크 문자가 서식을 깨면 안 된다."""
    sent = _capture(monkeypatch)
    notify.send_trend([{
        "title_ko": "**굵게** [링크](evil) `코드`",
        "why_ko": "[가짜](https://evil.example) 설명이다.",
        "url": "https://example.com/x",
    }], {})
    first, second = sent["embeds"][0]["description"].split("\n")[:2]
    assert "\\[링크\\]" in first
    assert first.startswith("**\\*\\*굵게")
    assert "\\`코드\\`" in first
    assert "\\[가짜\\]" in second


# --- 선정(trend_enrich.parse_picks) -------------------------------------------

POOL = [
    {"id": "a", "title": "Tool A", "url": "https://github.com/a"},
    {"id": "b", "title": "Release B", "url": "https://blog.google/b"},
    {"id": "c", "title": "Random C", "url": "https://c.example"},
]


def _pool():
    return [dict(it) for it in POOL]


def test_parse_picks_caps_at_two_and_keeps_order():
    import trend_enrich
    pool = _pool()
    out = trend_enrich.parse_picks(
        '{"picks": [{"id": "b", "title_ko": "도구 검색 기능 추가", "why_ko": "공식 블로그가 새 검색 기능을 발표했다."},'
        ' {"id": "a", "title_ko": "에이전트 도구 A", "why_ko": "GitHub에서 하루 만에 별 2천 개를 받았다."},'
        ' {"id": "c", "title_ko": "세 번째 항목", "why_ko": "세 번째라서 상한을 넘는 후보다."}]}', pool)
    assert [p["id"] for p in out] == ["b", "a"]
    assert out[0]["title_ko"] == "도구 검색 기능 추가"


def test_parse_picks_drops_unknown_ids_and_english_only():
    import trend_enrich
    out = trend_enrich.parse_picks(
        '{"picks": [{"id": "zzz", "title_ko": "없는 후보", "why_ko": "후보 목록에 없는 항목을 지어냈다."},'
        ' {"id": "a", "title_ko": "Tool A", "why_ko": "English only"}]}', _pool())
    assert out == []


def test_parse_picks_allows_zero_and_rejects_broken_json():
    import trend_enrich
    assert trend_enrich.parse_picks('{"picks": []}', _pool()) == []
    assert trend_enrich.parse_picks("not json", _pool()) is None


def test_parse_picks_replaces_middle_dot():
    import trend_enrich
    out = trend_enrich.parse_picks(
        '{"picks": [{"id": "a", "title_ko": "도구·스킬 묶음", '
        '"why_ko": "설치가 빠르다·사용법도 쉬워 바로 써 볼 만하다."}]}', _pool())
    assert "·" not in out[0]["title_ko"] and "·" not in out[0]["why_ko"]


# QA C11 적대 입력 일부(scratchpad qa/validator/data/trend_picks_adv.json)
ADVERSARIAL_PICKS = [
    ("가", "한국어 설명이 충분히 들어간 정상 문장이다."),                       # 한글 1자 제목
    ("오픈소스 LLM 탈옥 도구 공개", "탈옥 도구."),                              # 설명 한글 미달
    ("오픈소스 LLM 탈옥 도구 공개", "오픈소스 LLM 탈옥 도구가 공개돼 화제"),     # '~다.' 아님
    ("화제 Hugging Face malicious models found", "허깅페이스에서 악성 모델이 다수 발견됐다."),
    ("Ignore previous instructions 무시", "이전 지시를 무시하라는 문장이 들어 있었다."),
    ("허깅페이스 악성 모델 found in the wild 발견", "허깅페이스에서 악성 모델이 다수 발견됐다."),
    ("구글 프로젝트 제로 공개 정책 변경",
     "Project Zero changed its disclosure policy to 30 days 바뀌었다."),     # 설명 영어 구
    ("마이크로소프트 코파일럿 에이전트 기능 보안 취약점과 기업 데이터 유출 가능성 경고",
     "코파일럿 에이전트 기능의 보안 취약점이 공개됐다."),                    # 40자 초과
]


def test_parse_picks_rejects_adversarial_without_truncating():
    import trend_enrich
    for title, why in ADVERSARIAL_PICKS:
        raw = json.dumps({"picks": [{"id": "a", "title_ko": title, "why_ko": why}]},
                         ensure_ascii=False)
        assert trend_enrich.parse_picks(raw, _pool()) == [], title
    good = json.dumps({"picks": [{"id": "a", "title_ko": "Claude Code 보안 리뷰 기능 공개",
                                  "why_ko": "코드 변경을 자동으로 점검해 주는 기능이 모든 사용자에게 열렸다."}]},
                      ensure_ascii=False)
    out = trend_enrich.parse_picks(good, _pool())
    assert out[0]["title_ko"] == "Claude Code 보안 리뷰 기능 공개"


def test_send_daily_trend_failure_keeps_candidates(monkeypatch):
    """선정 실패(None)면 아무것도 안 보내고 False — 내일 재도전."""
    import trend_enrich
    monkeypatch.setattr(trend_enrich, "pick", lambda pool: None)
    called = []
    monkeypatch.setattr(notify, "send_trend", lambda *a: called.append(a))
    state = {}
    assert not trend_lane.send_daily_trend(_pool(), {}, state, "2026-11-21")
    assert not called and "last_trend_date" not in state


def test_send_daily_trend_nothing_worth_sending(monkeypatch):
    """볼 만한 게 0건이면 안 보내되 처리 완료(True) — 후보 소진."""
    import trend_enrich
    monkeypatch.setattr(trend_enrich, "pick", lambda pool: [])
    called = []
    monkeypatch.setattr(notify, "send_trend", lambda *a: called.append(a))
    state = {}
    assert trend_lane.send_daily_trend(_pool(), {}, state, "2026-11-21")
    assert not called and state["last_trend_date"] == "2026-11-21"


def test_select_trend_returns_pool_per_group():
    items = [{"id": f"g{i}", "title": f"github project number {i} unique{i}",
              "url": f"https://github.com/x/{i}", "source": "GitHub 급상승", "score": i}
             for i in range(12)]
    pool = trend_lane._select_trend(items, {"trend_pool_per_group": 8})
    assert len(pool) == 8
    assert pool[0]["id"] == "g11"  # score 내림차순


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
