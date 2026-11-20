"""2026-11-20 QA 디자인 수정 가드 — 링크 라벨 권고 번호(G3), 본문 넘침 시
용어와 WHY 생략(G1), 빈 footer 높이(G5).

렌더 테스트는 chromium이 없는 환경(CI 테스트 잡은 playwright 브라우저를
설치하지 않는다)에서는 건너뛴다."""
import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cardgen  # noqa: E402

ICSA_URL = "https://www.cisa.gov/news-events/ics-advisories/icsa-26-321-08"


# --- G3: CVE 코너 링크 라벨 ---------------------------------------------------

def test_advisory_label_starts_with_row_id():
    item = {"title": "Siemens SCALANCE W700", "url": ICSA_URL, "lane": "cve",
            "title_ko": "지멘스 SCALANCE W700 인증 우회 취약점"}
    assert cardgen._row_id(item) == "ICSA-26-321-08"
    assert cardgen.link_label(item) == "ICSA-26-321-08 지멘스 SCALANCE W700 인증 우회 취약점"


def test_cve_label_stays_cve_id_only():
    item = {"title": "CVE-2026-12345", "cvss": 9.8, "title_ko": "제품 원격 코드 실행"}
    assert cardgen.link_label(item) == "CVE-2026-12345"


def test_label_without_any_id_is_title_only():
    item = {"title": "한컴오피스 보안 업데이트 권고", "url": "https://www.boho.or.kr/x",
            "lane": "cve", "title_ko": "한컴오피스 임의 코드 실행 취약점"}
    assert cardgen._row_id(item) == cardgen.NO_ROW_ID
    assert cardgen.link_label(item) == "한컴오피스 임의 코드 실행 취약점"


def test_advisory_id_not_duplicated_when_title_has_it():
    item = {"title": "ICSA-26-321-08 Siemens", "url": ICSA_URL, "lane": "cve"}
    assert cardgen.link_label(item) == "ICSA-26-321-08 Siemens"


def test_news_label_unchanged_even_with_advisory_url():
    item = {"title": "t", "url": ICSA_URL, "title_ko": "산업제어 보안 동향", "summary_ko": "요약이다."}
    assert cardgen.link_label(item) == "산업제어 보안 동향"


# --- 렌더 공용 ------------------------------------------------------------------

@pytest.fixture(scope="module")
def browser():
    sync_api = pytest.importorskip("playwright.sync_api")
    pw = sync_api.sync_playwright().start()
    try:
        b = pw.chromium.launch()
    except Exception as exc:  # 브라우저 바이너리 미설치
        pw.stop()
        pytest.skip(f"chromium 실행 불가: {exc}")
    yield b
    b.close()
    pw.stop()


def _open(browser, tmp_path, page_html):
    page_html = page_html.replace("../assets/", Path(cardgen.ASSETS_DIR).as_uri() + "/")
    path = tmp_path / "card.html"
    path.write_text(page_html, encoding="utf-8")
    page = browser.new_page(viewport={"width": cardgen.CARD_WIDTH, "height": cardgen.CARD_HEIGHT})
    page.goto(path.as_uri())
    page.evaluate("() => document.fonts.ready")
    page.evaluate("() => fitAllCards()")
    return page


def _news_page(items):
    frags = cardgen._load_fragments()
    cards = [cardgen._build_news(frags, it, "2026.11.20", n=i, regions={},
                                 dots=cardgen._dots(frags, 4, i))
             for i, it in enumerate(items, start=1)]
    return cardgen._load_shell().replace("<!-- CARDS -->", "\n".join(cards))


MEASURE_JS = """(n) => {
  const card = document.getElementById('card-' + n);
  const over = [];
  card.querySelectorAll('.news-headline, .news-text, .why-text, .term-text').forEach((el) => {
    if (el.scrollHeight > el.clientHeight || el.scrollWidth > el.clientWidth)
      over.push(el.className + ' ' + el.scrollHeight + '/' + el.clientHeight);
  });
  return {over, text: card.querySelector('.news-text').innerText,
          why: !!card.querySelector('.why'), term: !!card.querySelector('.term')};
}"""

# QA s1_stress 5번 카드: 첫 문장 207자 + WHY + 용어 2줄 → 30px에서도 본문 넘침
LONG_FIRST = ("미국 사이버보안 인프라 보안국과 연방수사국은 중국 정부 지원을 받는 것으로 추정되는 공격 그룹이 "
              "통신사 코어 네트워크 장비와 합법 감청 시스템에 장기간 잠복하면서 정부 고위 인사와 기업 임원의 "
              "통화 기록, 문자 메시지 메타데이터, 일부 통화 녹음까지 수집했으며 이 과정에서 라우터 펌웨어 "
              "취약점과 관리 인터페이스 기본 계정을 함께 악용한 사실을 공동 권고문으로 확인했다.")


def _news(summary, title="통신사 코어망 장기 잠복 공격 그룹 감청 시스템까지 접근 미국 정부 공동 권고"):
    return {"title": "t", "url": "https://e.com", "source": "보안뉴스", "title_ko": title,
            "tags_ko": ["통신사해킹", "국가배후", "감청시스템"], "followup": True,
            "summary_ko": summary,
            "why_ko": "국내 통신사도 같은 장비를 써 관리 평면 분리 여부를 즉시 점검해야 한다는 경고다.",
            "term_ko": "관리 평면 — 네트워크 장비를 설정하고 감시하는 관리용 통신 경로로 사용자 트래픽과 분리해야 하는 영역"}


def test_long_first_sentence_drops_term_not_text(browser, tmp_path):
    page = _open(browser, tmp_path, _news_page([
        _news(LONG_FIRST + " 두 기관은 통신사에 관리 평면 분리를 권고했다."),
        _news("통신사 장비가 공격받았다. 두 기관이 권고했다.", title="통신사 장비 공격"),
    ]))
    long_card, short_card = page.evaluate(MEASURE_JS, 1), page.evaluate(MEASURE_JS, 2)
    page.close()
    assert long_card["over"] == []
    assert " ".join(long_card["text"].split()) == LONG_FIRST
    assert long_card["term"] is False and long_card["why"] is True
    # 짧은 본문은 아무것도 빼지 않는다
    assert short_card["over"] == [] and short_card["term"] and short_card["why"]


@pytest.mark.parametrize("length", [100, 160, 200, 230, 330])
def test_first_sentence_always_fully_visible(browser, tmp_path, length):
    base = re.sub(r"[.]", "", LONG_FIRST) * 2
    first = base[: length - 1].rstrip() + "."
    page = _open(browser, tmp_path, _news_page([_news(first + " 둘째 문장이다.")]))
    card = page.evaluate(MEASURE_JS, 1)
    page.close()
    assert card["over"] == []
    assert " ".join(card["text"].split()).startswith(first)


def test_empty_footer_keeps_same_height(browser, tmp_path, monkeypatch):
    captured = {}

    def fake_render(page_html, card_count):
        captured["html"] = page_html
        return [b""] * card_count

    monkeypatch.setattr(cardgen, "_render", fake_render)
    news = [{"title": "t", "url": "https://e.com", "title_ko": "쇼핑몰 회원 정보 유출",
             "summary_ko": "회원 정보가 유출됐다.", "source": "보안뉴스"}]
    # 회차 없는 표지(빈 footer) + 뉴스 + CVE 0건 카드(빈 footer)
    assert len(cardgen.build_cards(news, stats={})) == 3
    page = _open(browser, tmp_path, captured["html"])
    tops = page.evaluate("""() => Array.from(document.querySelectorAll('.card'), (c) =>
        c.querySelector('.bar-foot').getBoundingClientRect().top - c.getBoundingClientRect().top)""")
    page.close()
    assert len(set(tops)) == 1, tops


# --- 후속 pill(시안 g2_a), KEV 행(시안 g4_a), "실제 악용" 문구 -----------------

def _pills(item):
    frags = cardgen._load_fragments()
    card = cardgen._build_news(frags, item, "2026.11.20", n=1, regions={"보안뉴스": "국내"}, dots="")
    return re.findall(r'<span class="mono pill ([\w-]+)">(.*?)</span>', card)


def test_followup_pill_first_with_first_report_date_and_no_old_pill():
    pills = _pills({"title_ko": "제목", "summary_ko": "요약이다.", "source": "보안뉴스",
                    "tags_ko": ["랜섬웨어", "의료기관"], "followup": True, "kev": True,
                    "followup_of": {"date": "2026-11-16", "title_ko": "첫 보도"}})
    assert pills[0] == ("pill-follow", "후속 11.16")
    assert sum(1 for _, t in pills if t.startswith("후속")) == 1
    assert ("pill-urgent", "실제 악용") in pills


@pytest.mark.parametrize("of", [None, {"date": None}, {"date": "어제"}])
def test_followup_pill_without_date_is_plain(of):
    pills = _pills({"title_ko": "제목", "summary_ko": "요약이다.", "followup": True, "followup_of": of})
    assert pills[0] == ("pill-follow", "후속")


def test_no_followup_pill_when_not_followup():
    assert all(cls != "pill-follow" for cls, _ in _pills({"title_ko": "제목", "summary_ko": "요약이다."}))


def test_cve_card_sorts_kev_first_with_red_label_and_keeps_six_rows():
    frags = cardgen._load_fragments()
    rest = [{"title": f"CVE-2026-{1000 + i}", "cvss": 7.0, "title_ko": f"취약점 {i}", "kev": i in (6, 8)}
            for i in range(10)]
    card = cardgen._build_cve_list(frags, rest, "2026.11.20", n=1, dots="")
    heads = re.findall(r'<span class="mono cve-id">(.*?)</span><span class="mono cve-score">', card)
    assert len(heads) == 6 and "…외 4건" in card
    assert heads[0] == '<span class="cve-kev">실제 악용</span>CVE-2026-1006'
    assert heads[1] == '<span class="cve-kev">실제 악용</span>CVE-2026-1008'
    assert heads[2] == "CVE-2026-1000"
    assert card.count('class="cve-kev"') == 2


def test_template_has_no_old_kev_wording_on_screen():
    raw = open(cardgen.TEMPLATE_PATH, encoding="utf-8").read()
    visible = re.sub(r"/\*.*?\*/|<!--.*?-->", "", raw, flags=re.S)
    assert "실악용" not in visible
    assert ".cve-kev { color: #E74C3C;" in raw
