"""figure 전문 서브에이전트 — 이미지 없는 뉴스 카드용 SVG 다이어그램 생성.

og:image를 못 구한 뉴스 항목에 한해 Sonnet CLI(claude -p)로 기사의 사건
구조를 논문풍 다이어그램(SVG)으로 그린다. 키워드 나열(v17 흐름도)로는
"figure가 아니다"라는 사용자 결정에 따른 단계로, 흐름도는 폴백으로 남는다.

LLM 출력은 카드 HTML에 raw로 주입되므로 _validate_svg 화이트리스트
게이트를 통과한 것만 쓴다. 전 단계 fail-open — 토큰 없음·타임아웃·검증
실패 어느 것도 카드 발송을 막지 않고 기존 폴백 체인으로 흡수된다.
"""
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BASE_DIR / "figure_prompt.md"

DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_TIMEOUT = 120

# 카드 이미지 슬롯 실측(1080 - 좌우 패딩 64*2 = 952, 높이 340)과 1:1 —
# LLM이 다른 좌표계를 쓰면 레이아웃 보장이 깨지므로 viewBox는 강제한다
VIEWBOX = "0 0 952 340"
MAX_SVG_BYTES = 20 * 1024

_SVG_RE = re.compile(r"<svg[\s\S]*?</svg>", re.I)

# 정적 도형·텍스트만 허용 — 스크립트 실행(<script>), 외부 문서 삽입
# (<foreignObject>/<image>/href), CSS 주입(<style>·style 속성)은 렌더러가
# 로컬 chromium이라도 원천 차단한다 (LLM 출력 = 신뢰 불가 입력)
_ALLOWED_TAGS = {
    "svg", "g", "rect", "circle", "ellipse", "line", "polyline",
    "polygon", "path", "text", "tspan", "marker", "defs", "title",
}


def _validate_svg(svg: str) -> bool:
    """LLM이 만든 SVG의 구조 검증. 실패 시 False — 호출자는 폴백."""
    if len(svg.encode("utf-8")) > MAX_SVG_BYTES:
        return False
    try:
        root = ET.fromstring(svg)
    except ET.ParseError:
        return False
    if root.tag.split("}")[-1] != "svg":
        return False
    if root.get("viewBox") != VIEWBOX:
        return False
    for el in root.iter():
        tag = el.tag.split("}")[-1].lower()
        if tag not in _ALLOWED_TAGS:
            return False
        for attr in el.attrib:
            name = attr.split("}")[-1].lower()
            # on* 이벤트 핸들러, href류(외부 참조), style(CSS 주입) 금지
            if name.startswith("on") or name in ("href", "style"):
                return False
    return True


def _build_prompt(item: dict) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    title = (item.get("title_ko") or item.get("title") or "")[:200]
    # **키워드** 마커는 카드 본문용 — figure 입력에서는 걷어낸다
    summary = re.sub(r"\*\*", "", item.get("summary_ko") or item.get("summary") or "")[:500]
    tags = ", ".join(item.get("tags") or [])
    return (template
            .replace("{{TITLE}}", title)
            .replace("{{SUMMARY}}", summary)
            .replace("{{TAGS}}", tags))


def _generate_one(item: dict, model: str, timeout: int) -> str | None:
    try:
        proc = subprocess.run(
            [
                # librarian.summarize와 같은 순수 생성 호출 — 도구 불필요
                "claude", "-p", _build_prompt(item),
                "--model", model,
                "--output-format", "json",
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[figure] {item.get('id')} 실행 실패: {exc}", file=sys.stderr)
        return None

    if proc.returncode != 0:
        print(
            f"[figure] {item.get('id')} 비정상 종료 (code={proc.returncode}) "
            f"stderr: {proc.stderr[:300]}",
            file=sys.stderr,
        )
        return None

    try:
        result = json.loads(proc.stdout)["result"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"[figure] {item.get('id')} 파싱 실패: {exc}", file=sys.stderr)
        return None

    m = _SVG_RE.search(result or "")
    if not m:
        print(f"[figure] {item.get('id')} 응답에 SVG 없음", file=sys.stderr)
        return None
    svg = m.group(0)
    if not _validate_svg(svg):
        print(f"[figure] {item.get('id')} SVG 검증 탈락 — 키워드 흐름도 폴백", file=sys.stderr)
        return None
    return svg


def attach_figures(items: list[dict], config: dict, image_sources: set[str]) -> None:
    """to_send 뉴스 항목에 figure를 붙인다 (in-place).

    - og:image가 실제로 있는 항목은 그걸 쓴다: 여기서 선(先)다운로드해
      item["_img_path"]에 캐시 — LLM 호출 낭비와 렌더 때 중복 fetch 제거.
      fetch 실패는 item["_img_path"]=""로 기록해 렌더가 재시도하지 않는다.
    - 이미지를 못 구한 항목만 LLM으로 item["figure_svg"] 생성.
    """
    cfg = config.get("figure_agent") or {}
    if not cfg.get("enabled", True):
        return
    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        print("[figure] CLAUDE_CODE_OAUTH_TOKEN 미설정 — figure 스킵", file=sys.stderr)
        return

    import cardgen  # 지연 import: 순환 의존 방지 (main → figure → cardgen)

    model = cfg.get("model", DEFAULT_MODEL)
    timeout = int(cfg.get("timeout", DEFAULT_TIMEOUT))

    news = [it for it in items if not cardgen.is_cve_item(it)]
    made = 0
    for i, item in enumerate(news):
        if item.get("source") in image_sources:
            # 캐시 파일 번호는 렌더(_img_02~)와 겹치지 않게 50번대 사용
            path = cardgen._fetch_article_image(item, slot_index=50 + i)
            item["_img_path"] = path or ""
            if path:
                continue
        svg = _generate_one(item, model, timeout)
        if svg:
            item["figure_svg"] = svg
            made += 1
    if made:
        print(f"[figure] 다이어그램 {made}건 생성 (model={model})")
