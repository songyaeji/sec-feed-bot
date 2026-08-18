"""카드 최종 중복 게이트 — LLM 출력 정규화(librarian)와 적용 로직
(digest_select) 테스트. LLM 호출은 전부 모킹(오프라인 안전).

이 게이트가 막는 것: 백필 경로로 들어온 항목은 사서 판정이 없어 topic
slug 가드(_dedup_by_topic)를 아예 우회하고, 제목 토큰이 갈리면
_dedup_similar도 놓친다(NO.19 중복 카드). 발송 직전 마지막 겹.
"""
import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import digest_select  # noqa: E402
import librarian  # noqa: E402


def _item(item_id, title, importance=3, summary="본문 요약이 충분히 길다."):
    return {"id": item_id, "title": title, "importance": importance,
            "summary": summary, "url": f"https://example.com/{item_id}"}


# --- _clean_dedup_groups: LLM 출력 정규화 -----------------------------------

def test_clean_drops_singletons_and_out_of_range():
    got = librarian._clean_dedup_groups([[1, 2], [3], [9, 10], []], 5)
    assert got == [[1, 2]]


def test_clean_assigns_each_index_to_one_group_only():
    # 2가 두 묶음에 걸치면 앞선 묶음이 가져간다 — 안 그러면 대표 선정이 갈린다
    got = librarian._clean_dedup_groups([[1, 2], [2, 3]], 4)
    assert got == [[1, 2]]


def test_clean_rejects_bools_and_non_ints():
    # True는 파이썬에서 int 서브클래스 — 1번 항목으로 오인되면 안 된다
    assert librarian._clean_dedup_groups([[True, "2", None]], 4) == []


def test_clean_rejects_excessive_grouping():
    """'전부 같은 사건' 판정은 폐기 — 신뢰 불가 피드 입력의 카드 비우기 방어."""
    assert librarian._clean_dedup_groups([[1, 2, 3, 4, 5, 6]], 6) is None


def test_clean_accepts_at_threshold():
    # 6건 중 3건 삭제 = 정확히 상한(50%) — 폐기 아님
    assert librarian._clean_dedup_groups([[1, 2], [3, 4], [5, 6]], 6) == \
        [[1, 2], [3, 4], [5, 6]]


def test_clean_handles_non_list_payload():
    assert librarian._clean_dedup_groups({"groups": []}, 3) is None
    assert librarian._clean_dedup_groups(None, 3) is None


# --- dedup_gate: 호출 경계 --------------------------------------------------

def test_gate_skips_without_token():
    items = [_item("a", "A"), _item("b", "B")]
    with mock.patch.dict(os.environ, {}, clear=False):
        os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
        assert librarian.dedup_gate(items) is None


def test_gate_skips_single_item():
    # 1건이면 비교 대상이 없다 — LLM 콜 낭비 금지
    with mock.patch.object(librarian, "_run_claude_json") as run:
        assert librarian.dedup_gate([_item("a", "A")]) is None
        run.assert_not_called()


def test_gate_parses_groups_and_uses_dedup_model():
    proc = mock.Mock(returncode=0, stdout='{"result": "{\\"groups\\": [[1,2]]}"}',
                     stderr="")
    items = [_item("a", "A"), _item("b", "B"), _item("c", "C")]
    with mock.patch.dict(os.environ, {"CLAUDE_CODE_OAUTH_TOKEN": "t"}), \
            mock.patch.object(librarian, "_run_claude_json",
                              return_value=proc) as run:
        assert librarian.dedup_gate(items) == [[1, 2]]

    args = run.call_args[0][0]
    assert args == ["--model", librarian.DEDUP_MODEL]
    # 신뢰 불가 입력을 다루는 콜 — 도구를 하나도 주지 않는다(인젝션 표면)
    assert "--allowedTools" not in args


def test_gate_fails_open_on_bad_output():
    proc = mock.Mock(returncode=0, stdout="not json", stderr="")
    items = [_item("a", "A"), _item("b", "B")]
    with mock.patch.dict(os.environ, {"CLAUDE_CODE_OAUTH_TOKEN": "t"}), \
            mock.patch.object(librarian, "_run_claude_json", return_value=proc):
        assert librarian.dedup_gate(items) is None


# --- _apply_dedup_groups: 대표 선정 -----------------------------------------

def test_apply_keeps_highest_importance_per_group():
    items = [_item("a", "A", importance=2), _item("b", "B", importance=5),
             _item("c", "C", importance=4)]
    kept = digest_select._apply_dedup_groups(items, [[1, 2]])
    assert [it["id"] for it in kept] == ["b", "c"]


def test_apply_preserves_input_order():
    items = [_item(x, x.upper(), importance=i)
             for i, x in enumerate("abcd", start=1)]
    kept = digest_select._apply_dedup_groups(items, [[1, 4], [2, 3]])
    # 각 묶음 대표: d(importance 4), c(3) — 원래 순서 유지
    assert [it["id"] for it in kept] == ["c", "d"]


def test_apply_does_not_mutate_input():
    items = [_item("a", "A"), _item("b", "B", importance=5)]
    digest_select._apply_dedup_groups(items, [[1, 2]])
    assert [it["id"] for it in items] == ["a", "b"]


# --- _backfill_news: 슬롯 재충전 --------------------------------------------

def test_backfill_fills_to_cap_from_unjudged():
    selected = [_item("a", "완전히 다른 사건 하나")]
    ranked = selected + [_item("x", "국내 보험사 개인정보 유출"),
                         _item("y", "커널 드라이버 권한상승 취약점")]
    got = digest_select._backfill_news(selected, ranked, {"a"}, 3)
    assert [it["id"] for it in got] == ["a", "x", "y"]


def test_backfill_respects_excluded_ids():
    """게이트가 지운 항목이 백필로 되돌아오면 게이트가 무의미해진다."""
    selected = [_item("a", "완전히 다른 사건 하나")]
    ranked = selected + [_item("x", "국내 보험사 개인정보 유출")]
    got = digest_select._backfill_news(
        selected, ranked, set(), 3, excluded_ids={"x"})
    assert [it["id"] for it in got] == ["a"]


def test_backfill_skips_judged_and_uninformative():
    selected = [_item("a", "완전히 다른 사건 하나")]
    # j = 사서가 이미 판정(위키 전용으로 탈락한 것) — 백필 자격 없음
    # s = 요약이 제목과 같은 껍데기(구글뉴스류) — '제목=본문' 카드 방지
    shell = _item("s", "껍데기 제목")
    shell["summary"] = "껍데기 제목"
    ranked = selected + [_item("j", "판정된 뉴스"), shell]
    got = digest_select._backfill_news(selected, ranked, {"a", "j"}, 5)
    assert [it["id"] for it in got] == ["a"]


def test_backfill_does_not_mutate_input():
    selected = [_item("a", "완전히 다른 사건 하나")]
    ranked = selected + [_item("x", "국내 보험사 개인정보 유출")]
    digest_select._backfill_news(selected, ranked, set(), 3)
    assert len(selected) == 1
