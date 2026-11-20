"""사서의 위키 기록을 코드가 검증하고 보충하며, 위키를 Obsidian에서 바로 열리는
사건 기록으로 유지한다.

2026-11-20 점검 결과: 사서(Haiku)가 new·update로 답한 수보다 실제로 만들거나
고친 페이지가 매일 적었고(11-20 신규 26·갱신 9 답, 실제 생성 18·수정 8),
11-14 FBI 북한 4억 달러·11-16 SCKit은 카드로 나갔는데 위키 페이지가 아예
없었다. 모델이 규약 밖 파일(wiki/librarian_verdict.json)을 임의로 만든
흔적도 있었다. 판정과 기록이 어긋나면 위키는 사건 기록으로 쓸 수 없다.

같은 날 QA(docs/qa/2026-11-20-qa-results.md E1~E8)에서 추가로 확인한 구멍:
발행 뉴스 217건 중 112건 위키 누락, 대문자 slug 8개 미검색과 Windows 덮어쓰기,
없는 파일을 가리키는 링크 126개, 앵커 링크 미변환과 코드 span 변환, 타임라인
하위 줄 이동, Obsidian 태그 규칙 위반 201개, 중복 페이지와 slug 충돌.

digest 한 번에 이렇게 돈다.
1. maintenance(원장): 사서 실행 전. 멱등 정비 단계를 정해진 순서로 실행한다.
   중복 페이지 병합, slug 충돌 분리, 대문자 파일명 소문자화, 원장 소급 기록,
   frontmatter 태그 정리, 링크 정리. 바뀔 것이 없으면 아무것도 쓰지 않는다.
2. snapshot / snapshot_protected: 사서 실행 직전.
3. restore_protected / remove_stray: 사서 실행 직후. CLAUDE.md와 INDEX를
   원래대로 되돌리고 규약 밖 새 파일을 지운다.
4. ensure_recorded: 사서 문안 병합 뒤, 그리고 발송 확정 뒤(sent=True).
   페이지나 타임라인 줄이 없으면 코드가 직접 쓴다.

위키 페이지는 사고, 법제도, 기관 발표만 만든다(kind incident, policy,
institution, 사용자 결정 2026-11-20). kind를 모르면 기록한다.
"""
import glob
import hashlib
import math
import os
import re
import sys
from collections import Counter
from datetime import date, timedelta
from urllib.parse import urlparse

import dedup as dedup_lib
from wiki_index import TOPICS_DIR, WIKI_DIR

WIKI_KINDS = {"incident", "policy", "institution"}
KNOWN_KINDS = WIKI_KINDS | {"vuln", "other"}
# 사서가 목록 밖 값을 내도 같은 뜻이면 받아 준다. main.py와 공유한다
_KIND_SYNONYMS = {
    "incident": "incident", "incidents": "incident", "breach": "incident",
    "data_breach": "incident", "attack": "incident", "cyberattack": "incident",
    "hack": "incident", "hacking": "incident", "leak": "incident",
    "compromise": "incident", "ransomware": "incident", "outage": "incident",
    "사고": "incident", "침해": "incident",
    "policy": "policy", "policies": "policy", "regulation": "policy",
    "law": "policy", "legal": "policy", "legislation": "policy",
    "sanction": "policy", "법제도": "policy", "정책": "policy",
    "institution": "institution", "institutional": "institution",
    "agency": "institution", "government": "institution", "기관": "institution",
    "vuln": "vuln", "vulnerability": "vuln", "vulnerabilities": "vuln",
    "cve": "vuln", "patch": "vuln", "advisory": "vuln", "exploit": "vuln",
    "취약점": "vuln",
    "other": "other", "misc": "other", "promo": "other", "promotion": "other",
    "column": "other", "opinion": "other", "기타": "other",
}

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,80}$")
_ALLOWED_ROOT = {"INDEX.md", "INDEX-archive.md", "CLAUDE.md"}
# 사서가 고칠 수 없는 파일. 실행 전 내용을 찍어 두고 실행 뒤 되돌린다
PROTECTED = ("CLAUDE.md", "INDEX.md", "INDEX-archive.md")

# 사용자가 확정한 중복 병합 7그룹(2026-11-20 QA E8). 흡수 페이지 → 정본
MERGES = {
    "2026-10-knx-protocol-account-lockout": "2026-07-knx-protocol-lockout",
    "2026-08-chaindrop-analysis-update": "2026-08-chaindrop-npm-propagating-malware",
    "2026-07-openshift-guardrails-redos": "2026-07-openshift-ai-redos",
    "2026-07-onnx-version-converter-uaf": "2026-07-onnx-upsample-null-deref",
    "2026-11-nAble-n-central-auth-bypass": "2026-08-n-central-auth-bypass",
    "2026-08-gocaracal-dark-caracal-malware": "2026-08-dark-caracal-gocaracal",
    "2026-09-court-ssn-encryption-supreme": "2026-09-court-ssn-encryption-admin",
}
# 같은 slug에 다른 사건(CVE 다름)이 걸린 3쌍. 나중 페이지에 CVE 번호를 붙인다
SLUG_RENAMES = {
    "2026-09-velocloud-orchestrator-rce": "2026-09-velocloud-orchestrator-rce-93952",
    "2026-11-oracle-platform-security-rce": "2026-11-oracle-platform-security-rce-114824",
    "2026-10-comfast-cf-n1-s-command-injection":
        "2026-10-comfast-cf-n1-s-command-injection-77683",
}


def _strip_month(name: str) -> str:
    return re.sub(r"^\d{4}-\d{2}-", "", name)


def _aliases() -> dict[str, str]:
    """옛 파일명과 옛 slug(소문자) → 정본 파일명. 링크와 find_topic이 쓴다."""
    out = {}
    for old, new in MERGES.items():
        out[old.lower()] = new
        out[_strip_month(old).lower()] = new
    for old, new in SLUG_RENAMES.items():
        out[old.lower()] = new  # 옛 slug는 앞 페이지가 그대로 쓴다
    return out


def normalize_kind(value) -> str | None:
    """사서 kind 값을 incident, policy, institution, vuln, other 중 하나로.

    대소문자와 공백을 정리하고 같은 뜻의 값(breach 등)을 맞춘다. 모르는 값이나
    문자열이 아니면 None."""
    if not isinstance(value, str):
        return None
    key = re.sub(r"[\s-]+", "_", value.strip().lower())
    return _KIND_SYNONYMS.get(key)


# ------------------------------------------------------------ 파일 목록

def snapshot() -> set[str]:
    """wiki/ 아래 파일 상대경로 집합 — 사서 실행 전에 찍어 둔다."""
    out = set()
    for root, _, files in os.walk(WIKI_DIR):
        for name in files:
            out.add(os.path.relpath(os.path.join(root, name), WIKI_DIR).replace("\\", "/"))
    return out


def _allowed(rel: str) -> bool:
    if rel in _ALLOWED_ROOT or rel == "topics/.gitkeep":
        return True
    return rel.startswith("topics/") and rel.endswith(".md") and rel.count("/") == 1


def remove_stray(before: set[str]) -> list[str]:
    """이번 실행에서 새로 생긴 규약 밖 파일을 지운다. 지운 목록 반환."""
    removed = []
    for rel in sorted(snapshot() - before):
        if _allowed(rel):
            continue
        try:
            os.remove(os.path.join(WIKI_DIR, rel))
            removed.append(rel)
        except OSError:
            continue
    if removed:
        print(f"[wiki] 규약 밖 파일 삭제: {removed}", file=sys.stderr)
    return removed


def snapshot_protected() -> dict[str, bytes | None]:
    """보호 파일(CLAUDE.md, INDEX.md, INDEX-archive.md)의 현재 내용."""
    out: dict[str, bytes | None] = {}
    for rel in PROTECTED:
        try:
            with open(os.path.join(WIKI_DIR, rel), "rb") as f:
                out[rel] = f.read()
        except OSError:
            out[rel] = None
    return out


def restore_protected(snap: dict[str, bytes | None]) -> list[str]:
    """사서가 바꾼 보호 파일을 실행 전 내용으로 되돌린다. 되돌린 목록 반환."""
    restored = []
    for rel, data in snap.items():
        path = os.path.join(WIKI_DIR, rel)
        try:
            with open(path, "rb") as f:
                now = f.read()
        except OSError:
            now = None
        if now == data:
            continue
        try:
            if data is None:
                os.remove(path)
            else:
                with open(path, "wb") as f:
                    f.write(data)
            restored.append(rel)
        except OSError:
            continue
    if restored:
        print(f"[wiki] 사서가 바꾼 보호 파일 복원: {restored}", file=sys.stderr)
    return restored


# ------------------------------------------------------------ 토픽 파일

def topic_files() -> dict[str, str]:
    """파일명(확장자 없음) → 경로."""
    return {os.path.basename(p)[:-3]: p
            for p in glob.glob(os.path.join(TOPICS_DIR, "*.md"))}


def find_topic(slug: str, files: dict[str, str]) -> str | None:
    """slug로 토픽 파일 찾기. 대소문자 무시.

    파일명이 slug이거나 'YYYY-MM-slug'인 것, 여럿이면 최신. 병합이나 분리로
    바뀐 옛 이름은 정본 파일명으로 이어 준다."""
    if not isinstance(slug, str):
        return None
    key = slug.strip().lower()
    if not key:
        return None
    lower = {n.lower(): n for n in files}
    alias = _aliases().get(key)
    if alias and alias.lower() in lower:
        return lower[alias.lower()]
    if key in lower:
        return lower[key]
    pat = re.compile(rf"\d{{4}}-\d{{2}}-{re.escape(key)}")
    hits = sorted(n for n in files if pat.fullmatch(n.lower()))
    return hits[-1] if hits else None


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ------------------------------------------------------------ frontmatter

_FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
_BLOCK_ITEM_RE = re.compile(r"^\s*-(?:\s+(.*))?$")


def _split_fm(text: str) -> tuple[str | None, str]:
    m = _FM_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def _join_fm(fm: str, rest: str) -> str:
    return f"---\n{fm}\n---\n{rest}"


def _fm_list(fm: str, key: str) -> list[str] | None:
    """`key: [a, b]`와 블록 목록(`key:` 다음 `  - a`)을 모두 읽는다. 키가 없으면 None."""
    lines = fm.split("\n")
    for i, line in enumerate(lines):
        m = re.match(rf"{re.escape(key)}:\s*(.*)$", line)
        if not m:
            continue
        val = m.group(1).strip()
        if val.startswith("["):
            inner = val[1:val.rfind("]")] if "]" in val else val[1:]
            parts = [p.strip().strip("'\"").strip() for p in inner.split(",")]
            return [p for p in parts if p]
        if val:
            return [val.strip("'\"")]
        items = []
        for nxt in lines[i + 1:]:
            mm = _BLOCK_ITEM_RE.match(nxt)
            if not mm:
                break
            if (mm.group(1) or "").strip():
                items.append(mm.group(1).strip().strip("'\""))
        return items
    return None


def _set_fm_list(fm: str, key: str, values: list[str]) -> str:
    """key 줄(블록 목록이면 딸린 줄까지)을 `key: [a, b]` 한 줄로 바꾼다."""
    lines = fm.split("\n")
    out: list[str] = []
    done = False
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not done and re.match(rf"{re.escape(key)}:", line):
            out.append(f"{key}: [{', '.join(values)}]")
            done = True
            if not line.split(":", 1)[1].strip():
                while i < len(lines) and _BLOCK_ITEM_RE.match(lines[i]):
                    i += 1
            continue
        out.append(line)
    if not done:
        out.append(f"{key}: [{', '.join(values)}]")
    return "\n".join(out)


def _set_slug(text: str, slug: str) -> str:
    fm, rest = _split_fm(text)
    if fm is None:
        return text
    if re.search(r"^slug:", fm, re.M):
        fm = re.sub(r"^slug:.*$", f"slug: {slug}", fm, count=1, flags=re.M)
    else:
        fm = f"slug: {slug}\n{fm}"
    return _join_fm(fm, rest)


def _fm_slug(text: str) -> str:
    fm, _ = _split_fm(text)
    m = re.search(r"^slug:\s*(.*)$", fm or "", re.M)
    return m.group(1).strip().strip("'\"") if m else ""


def normalize_tag(tag) -> str:
    """Obsidian 태그 규칙에 맞춘 태그. 못 살리면 빈 문자열.

    Obsidian 태그는 글자, 숫자, _, -, / 만 쓰고 숫자만으로는 안 된다.
    공백은 없애고, ++는 pp, 숫자 사이 마침표는 _, 가운뎃점은 - 로 바꾸고,
    나머지 허용 밖 문자는 지운다."""
    if tag is None:
        return ""
    s = str(tag).strip().lstrip("#")
    s = s.replace("++", "pp")
    s = re.sub(r"(?<=\d)\.(?=\d)", "_", s)
    s = s.replace("·", "-")
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[^\w/-]", "", s)
    s = re.sub(r"-{2,}", "-", s).strip("-/")
    if not s or re.fullmatch(r"[\d_]+", s):
        return ""
    return s


def normalize_tags(tags) -> list[str]:
    """태그 목록 정리. 정리 뒤 같은 태그(대소문자 무시)는 하나만 남긴다."""
    out: list[str] = []
    seen: set[str] = set()
    for t in tags or []:
        n = normalize_tag(t)
        if n and n.lower() not in seen:
            seen.add(n.lower())
            out.append(n)
    return out


# ------------------------------------------------------------ 링크

_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)[^\n]*?(?<!`)\1(?!`)")
_WIKILINK_RE = re.compile(r"(!?)\[\[([^\[\]\n]*)\]\]")


def _outside_code(text: str, fn) -> str:
    """펜스 코드 블록과 인라인 코드 span 밖의 글에만 fn을 적용한다."""
    out: list[str] = []
    plain: list[str] = []
    fence = None

    def flush():
        chunk = "".join(plain)
        plain.clear()
        pos = 0
        for m in _CODE_SPAN_RE.finditer(chunk):
            out.append(fn(chunk[pos:m.start()]))
            out.append(m.group(0))
            pos = m.end()
        out.append(fn(chunk[pos:]))

    for line in text.splitlines(keepends=True):
        m = _FENCE_RE.match(line)
        if fence is None:
            if m:
                flush()
                fence = m.group(1)
                out.append(line)
            else:
                plain.append(line)
            continue
        out.append(line)
        if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                and not line.strip().strip(fence[0]):
            fence = None
    if fence is None:
        flush()
    else:
        out.extend(plain)
    return "".join(out)


def _resolve(target: str, files: dict[str, str]) -> str | None:
    t = target.strip()
    if t.lower().endswith(".md"):
        t = t[:-3]
    t = t.replace("\\", "/").rsplit("/", 1)[-1].strip()
    if not t:
        return None
    if t in files:
        return t
    return find_topic(t, files)


def _rewrite_links(text: str, files: dict[str, str]) -> tuple[str, int, int]:
    """[[링크]]를 Obsidian이 여는 정확한 파일명으로 고친다.

    [[slug]], [[slug#제목]], [[slug|별칭]] 모두 처리한다. 대상 파일이 없으면
    링크를 풀어 글자만 남긴다(별칭이 있으면 별칭). 코드 안은 건드리지 않는다.
    (고친 텍스트, 고친 링크 수, 푼 링크 수)."""
    counts = [0, 0]

    def repl(m):
        if m.group(1):  # ![[...]] 임베드는 그대로
            return m.group(0)
        inner = m.group(2)
        target, sep, alias = inner.partition("|")
        base, hsep, heading = target.partition("#")
        if not base.strip():  # [[#제목]] 같은 페이지 앵커
            return m.group(0)
        name = _resolve(base, files)
        if name is None:
            counts[1] += 1
            return (alias.strip() if sep and alias.strip() else base.strip())
        new = f"[[{name}{hsep}{heading}{sep}{alias}]]"
        if new != m.group(0):
            counts[0] += 1
        return new

    fixed = _outside_code(text, lambda chunk: _WIKILINK_RE.sub(repl, chunk))
    return fixed, counts[0], counts[1]


def fix_links(text: str, files: dict[str, str]) -> str:
    """[[slug]] → [[YYYY-MM-slug]], 없는 대상 링크는 글자로 (Obsidian은 파일명으로만 연다)."""
    return _rewrite_links(text, files)[0]


def migrate_links(stats: dict | None = None) -> int:
    """전 페이지 링크 정리. 바뀐 페이지 수. stats가 있으면 링크 수를 더한다."""
    files = topic_files()
    changed = 0
    for name, path in files.items():
        text = _read(path)
        fixed, relinked, unlinked = _rewrite_links(text, files)
        if fixed != text:
            _write(path, fixed)
            changed += 1
        if stats is not None:
            stats["links_relinked"] = stats.get("links_relinked", 0) + relinked
            stats["links_unlinked"] = stats.get("links_unlinked", 0) + unlinked
    return changed


# ------------------------------------------------------------ 타임라인

_TL_HEAD_RE = re.compile(r"^## 타임라인[ \t]*$", re.M)
_NEXT_HEAD_RE = re.compile(r"^## ", re.M)
_LINE_URL_RE = re.compile(r"\]\((\S+?)\)")
_HANGUL_RE = re.compile(r"[가-힣]")


def _timeline_parts(text: str):
    """(앞부분, 타임라인 구역 본문, 뒷부분) 또는 None."""
    m = _TL_HEAD_RE.search(text)
    if not m:
        return None
    nxt = _NEXT_HEAD_RE.search(text, m.end())
    end = nxt.start() if nxt else len(text)
    return text[:m.start()], text[m.end():end], text[end:]


def _blocks(section: str) -> tuple[list[str], list[list[str]]]:
    """타임라인 구역을 (머리 줄, 항목 블록)으로 나눈다.

    '- '로 시작하는 줄이 블록을 열고, 뒤따르는 들여쓴 하위 줄과 빈 줄은 그
    블록에 붙는다. 정렬할 때 하위 줄이 부모를 떠나지 않게 한다."""
    lines = section.strip("\n").split("\n") if section.strip() else []
    pre: list[str] = []
    blocks: list[list[str]] = []
    for line in lines:
        if line.startswith("- "):
            blocks.append([line])
        elif blocks:
            blocks[-1].append(line)
        else:
            pre.append(line)
    for b in blocks:
        while len(b) > 1 and not b[-1].strip():
            b.pop()
    while pre and not pre[-1].strip():
        pre.pop()
    return pre, blocks


def _block_url(block: list[str]) -> str:
    m = _LINE_URL_RE.search(block[0])
    return m.group(1) if m else ""


def _add_timeline(text: str, new_blocks: list[list[str]]) -> str:
    """'## 타임라인'에 블록을 넣고 날짜순(안정 정렬)으로 맞춘다. 구역이 없으면 만든다."""
    parts = _timeline_parts(text)
    if parts is None:
        lines = "\n".join(ln for b in new_blocks for ln in b)
        section = f"## 타임라인\n\n{lines}\n\n"
        anchor = re.search(r"^## 관련", text, re.M)
        if anchor:
            return text[:anchor.start()] + section + text[anchor.start():]
        return text.rstrip("\n") + "\n\n" + section
    head, section, tail = parts
    pre, blocks = _blocks(section)
    blocks.extend(new_blocks)
    # 같은 날짜 줄은 기존 순서 뒤에 붙는다
    blocks.sort(key=lambda b: b[0][2:12])
    body = "\n".join([*pre, *(ln for b in blocks for ln in b)]).strip("\n")
    return f"{head}## 타임라인\n\n{body}\n" + (f"\n{tail}" if tail else "")


def _insert_timeline(text: str, line: str) -> str:
    return _add_timeline(text, [[line]])


def _url_key(url: str) -> str:
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://(www\.)?", "", u)
    return u.split("#", 1)[0].rstrip("/")


def _timeline_urls(text: str) -> set[str]:
    parts = _timeline_parts(text)
    if parts is None:
        return set()
    _, blocks = _blocks(parts[1])
    return {_url_key(u) for u in (_block_url(b) for b in blocks) if u}


# ------------------------------------------------------------ 페이지 병합과 이름 정리

def _related_drop_links_to(text: str, names: set[str]) -> str:
    """'## 관련' 구역에서 names(소문자 파일명이나 slug)만 가리키는 줄을 뺀다."""
    m = re.search(r"^## 관련[ \t]*$", text, re.M)
    if not m:
        return text
    nxt = _NEXT_HEAD_RE.search(text, m.end())
    end = nxt.start() if nxt else len(text)
    kept = []
    for line in text[m.end():end].split("\n"):
        targets = [t.partition("|")[0].partition("#")[0].strip().lower()
                   for t in re.findall(r"\[\[([^\[\]\n]*)\]\]", line)]
        if targets and all(t in names or _strip_month(t) in names for t in targets):
            continue
        kept.append(line)
    return text[:m.end()] + "\n".join(kept) + text[end:]


def _merge_into(target: str, source: str, source_name: str, target_name: str) -> str:
    """source 페이지를 target에 합친다. 타임라인은 URL 기준 중복 제거 뒤 날짜순,
    tags와 cves는 합집합. target의 요약과 본문은 그대로 둔다."""
    tparts = _timeline_parts(target)
    have_urls = _timeline_urls(target)
    have_lines = set()
    if tparts:
        have_lines = {b[0].strip() for b in _blocks(tparts[1])[1]}
    add: list[list[str]] = []
    sparts = _timeline_parts(source)
    for b in (_blocks(sparts[1])[1] if sparts else []):
        key = _url_key(_block_url(b))
        if (key and key in have_urls) or (not key and b[0].strip() in have_lines):
            continue
        add.append(b)
        if key:
            have_urls.add(key)
        have_lines.add(b[0].strip())
    text = _add_timeline(target, add) if add else target

    fm, rest = _split_fm(text)
    sfm, _ = _split_fm(source)
    if fm is not None and sfm is not None:
        tags = _fm_list(fm, "tags") or []
        merged_tags = normalize_tags(tags + (_fm_list(sfm, "tags") or []))
        if merged_tags != tags:
            fm = _set_fm_list(fm, "tags", merged_tags)
        cves = _fm_list(fm, "cves") or []
        merged_cves = list(dict.fromkeys(c.upper() for c in cves + (_fm_list(sfm, "cves") or [])))
        if merged_cves != cves:
            fm = _set_fm_list(fm, "cves", merged_cves)
        text = _join_fm(fm, rest)
    # 흡수된 페이지를 가리키던 관련 줄은 이제 자기 자신이라 뺀다
    drop = {source_name.lower(), _strip_month(source_name).lower(),
            _fm_slug(source).lower(), target_name.lower()}
    return _related_drop_links_to(text, {d for d in drop if d})


def merge_duplicates() -> int:
    """MERGES의 흡수 페이지를 정본에 합치고 지운다. 합친 페이지 수(멱등)."""
    files = topic_files()
    lower = {n.lower(): n for n in files}
    merged = 0
    for src, dst in MERGES.items():
        s, d = lower.get(src.lower()), lower.get(dst.lower())
        if not s or not d or s == d:
            continue
        _write(files[d], _merge_into(_read(files[d]), _read(files[s]), s, d))
        os.remove(files[s])
        merged += 1
        print(f"[wiki] 중복 페이지 병합: {s} → {d}", file=sys.stderr)
    return merged


def rename_collisions() -> int:
    """SLUG_RENAMES의 나중 페이지에 다른 slug를 준다(파일명과 frontmatter). 멱등."""
    files = topic_files()
    lower = {n.lower(): n for n in files}
    renamed = 0
    for old, new in SLUG_RENAMES.items():
        o = lower.get(old.lower())
        if not o or new.lower() in lower:
            continue
        _write(os.path.join(TOPICS_DIR, f"{new}.md"),
               _set_slug(_read(files[o]), _strip_month(new)))
        os.remove(files[o])
        renamed += 1
        print(f"[wiki] slug 충돌 분리: {o} → {new}", file=sys.stderr)
    return renamed


def lowercase_names() -> int:
    """대문자가 섞인 파일명과 frontmatter slug를 소문자로. 바꾼 페이지 수(멱등).

    대소문자만 다른 파일이 따로 있으면(Linux) 새 파일을 만들지 않고 소문자
    파일로 합친다. Windows와 macOS에서는 대소문자만 바꾸는 rename이 된다."""
    changed = 0
    for name, path in sorted(topic_files().items()):
        text = _read(path)
        slug = _fm_slug(text)
        fixed = _set_slug(text, slug.lower()) if slug != slug.lower() else text
        low = name.lower()
        if low == name:
            if fixed != text:
                _write(path, fixed)
                changed += 1
            continue
        new_path = os.path.join(TOPICS_DIR, f"{low}.md")
        if os.path.exists(new_path) and not os.path.samefile(path, new_path):
            _write(new_path, _merge_into(_read(new_path), fixed, name, low))
            os.remove(path)
        else:
            os.rename(path, new_path)
            _write(new_path, fixed)
        changed += 1
        print(f"[wiki] 파일명 소문자화: {name} → {low}", file=sys.stderr)
    return changed


def fix_tags(stats: dict | None = None) -> int:
    """frontmatter tags를 Obsidian 태그 규칙에 맞춘다. 바뀐 페이지 수(멱등)."""
    changed = 0
    for path in topic_files().values():
        text = _read(path)
        fm, rest = _split_fm(text)
        if fm is None:
            continue
        tags = _fm_list(fm, "tags")
        if tags is None:
            continue
        fixed = normalize_tags(tags)
        if fixed == tags:
            continue
        _write(path, _join_fm(_set_fm_list(fm, "tags", fixed), rest))
        changed += 1
        if stats is not None:
            stats["tag_values_fixed"] = stats.get("tag_values_fixed", 0) + sum(
                1 for t in tags if normalize_tag(t) != t)
    return changed


# ------------------------------------------------------------ 기존 페이지 찾기

_TOKEN_RE = re.compile(r"[a-z0-9]+|[가-힣]+")
_JOSA = ("으로부터", "에게서", "으로써", "에서는", "에게는", "으로", "에서", "에게",
         "부터", "까지", "라는", "이라", "과의", "와의", "의", "은", "는", "이",
         "가", "을", "를", "로", "에", "과", "와", "도", "만")
_STOP = set("""
the and for with from into over after amid via new are was has have its this that
how why what who says said will can more than about use uses used using attack
attacks hacker hackers hack hacked security vulnerability vulnerabilities flaw flaws
patch patches patched exploit exploited exploits critical zero day days data breach
breaches cve cvss rce html www com news article warns warning report reports update
updates released release fixes fix issues issue
보안 해킹 사고 피해 취약점 패치 공격 침해 유출 개인정보 정보 관련 공개 발표 확인 주의
경고 대응 긴급 가능 발견 기업 업체 고객 서비스 시스템 국내 해외 정부 이후 통해 위해
대한 따라 악용 실제 조사 사건 최대 이상 규모 추가 사용 공격자 해커 수법 사례 주장
""".split())
_WINDOW_BEFORE = 30  # 기록일 기준 앞 30일 안에 타임라인 줄이 있는 페이지만 후보
_WINDOW_AFTER = 3
_ANCHOR_MAX_PAGES = 5  # slug나 tags의 고유명 토큰이 이 수 이하 페이지에만 있어야 한다
_RARE_MAX_PAGES = 5  # 드문 낱말 기준(페이지 수)
_MARGIN = 1.5  # 1위 점수가 2위의 몇 배 이상이어야 붙인다
_MARGIN_ONE_RARE = 2.0  # 드문 낱말이 하나뿐이면 더 큰 차이를 요구한다
_LATIN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]{3,}")


def _strip_josa(token: str) -> str:
    for josa in _JOSA:
        if token.endswith(josa) and len(token) - len(josa) >= 2:
            return token[: -len(josa)]
    return token


def _tokens(text: str) -> set[str]:
    out = set()
    for w in _TOKEN_RE.findall((text or "").lower()):
        if "가" <= w[0] <= "힣":
            w = _strip_josa(w)
            if len(w) < 2:
                continue
        elif w.isdigit() or (len(w) < 3 and w.isalpha()):
            continue
        if w not in _STOP:
            out.add(w)
    return out


def _name_like(w: str) -> bool:
    """고유명일 만한 길이. 영문 4자 이상이나 한글 3자 이상."""
    return len(w) >= (3 if "가" <= w[0] <= "힣" else 4)


def _parse_date(value) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _first_sentence(text: str) -> str:
    text = " ".join((text or "").split())
    m = re.search(r"^(.*?[.!?다])(\s|$)", text)
    return m.group(1) if m else text


class _PageIndex:
    """원장 항목이나 발송 항목이 어느 기존 페이지의 사건인지 찾는 색인.

    잘못 붙이는 것이 새 페이지를 만드는 것보다 나쁘다. 그래서 확실한 신호만
    쓴다. URL이 이미 한 페이지에만 있음, CVE 교집합, 또는 아래를 모두 만족할 때.
    1. 후보는 기록일 앞 30일부터 뒤 3일 사이에 타임라인 줄이 있고, 한국어
       제목에 든 영문 고유명(4자 이상)이 모두 있는 페이지다. RUGGEDCOM
       CROSSBOW가 RUGGEDCOM APE1808 페이지에 붙는 것을 막는다.
    2. 겹치는 낱말 점수(드문 낱말일수록 큼) 1위가 2위의 1.5배 이상이고
       낱말이 둘 이상 겹친다.
    3. 그 페이지의 slug나 tags에 있는 드문 고유명이 겹치거나, 위키 전체에서
       드문 낱말이 둘 이상 겹친다. 드문 낱말이 하나뿐이면 2위의 2배 이상."""

    def __init__(self, files: dict[str, str]):
        self.pages: dict[str, dict] = {}
        self.df: Counter = Counter()   # 낱말이 든 페이지 수
        self.adf: Counter = Counter()  # 낱말이 slug나 tags에 든 페이지 수
        for name, path in files.items():
            try:
                self.update(name, _read(path))
            except OSError:
                continue

    def update(self, name: str, text: str) -> None:
        old = self.pages.get(name)
        if old:
            self.df.subtract(old["tokens"])
            self.adf.subtract(old["anchors"])
        fm, body = _split_fm(text)
        fm = fm or ""
        tags = " ".join(_fm_list(fm, "tags") or [])
        cves = {c.upper() for c in (_fm_list(fm, "cves") or [])}
        summary = ""
        for para in body.split("\n\n"):
            s = para.strip()
            if s and not s.startswith("#") and not s.startswith("- "):
                summary = s.replace("**", "")
                break
        dates, facts = set(), []
        parts = _timeline_parts(text)
        for b in (_blocks(parts[1])[1] if parts else []):
            d = _parse_date(b[0][2:12])
            if d:
                dates.add(d)
            facts.append(" ".join(b).split("—", 1)[-1])
        fs = _parse_date((re.search(r"^first_seen:\s*(\S+)", fm, re.M) or [None, ""])[1])
        if fs:
            dates.add(fs)
        slug_words = _strip_month(name).replace("-", " ")
        info = {
            "dates": dates,
            "last": max(dates) if dates else date.min,
            "cves": cves,
            "urls": {_url_key(u) for u in _LINE_URL_RE.findall(text)},
            "tokens": _tokens(f"{slug_words} {tags} {summary} {' '.join(facts)}"),
            "anchors": _tokens(f"{slug_words} {tags}"),
        }
        info["tokens"] |= info["anchors"]
        self.pages[name] = info
        self.df.update(info["tokens"])
        self.adf.update(info["anchors"])

    def _idf(self, w: str) -> float:
        return math.log((len(self.pages) + 1) / (max(self.df[w], 0) + 1)) + 1

    def match(self, entry: dict) -> str | None:
        key = _url_key(entry.get("url") or "")
        if key:
            hits = [n for n, p in self.pages.items() if key in p["urls"]]
            if len(hits) == 1:
                return hits[0]
        text = " ".join(str(entry.get(k) or "") for k in
                        ("title", "title_ko", "summary", "summary_ko"))
        raw = entry.get("cves")
        cves = {c.upper() for c in raw if isinstance(c, str)} if isinstance(raw, list) else set()
        cves |= dedup_lib.extract_cves(text)
        if cves:
            scored = [(len(cves & p["cves"]), p["last"], n)
                      for n, p in self.pages.items() if cves & p["cves"]]
            if scored:
                return max(scored)[2]
        d0 = _parse_date(entry.get("date"))
        if d0 is None:
            return None
        lo, hi = d0 - timedelta(days=_WINDOW_BEFORE), d0 + timedelta(days=_WINDOW_AFTER)
        words = _tokens(" ".join(str(entry.get(k) or "") for k in
                                 ("title", "title_ko", "summary_ko")))
        latin = {w.lower() for w in _LATIN_RE.findall(str(entry.get("title_ko") or ""))}
        latin = {w for w in latin if w not in _STOP and not w.isdigit()}
        scored = []
        for n, p in self.pages.items():
            if not any(lo <= d <= hi for d in p["dates"]) or not latin <= p["tokens"]:
                continue
            shared = words & p["tokens"]
            if shared:
                scored.append((sum(self._idf(w) for w in shared), n, shared))
        scored.sort(key=lambda s: s[0], reverse=True)
        if not scored:
            return None
        ratio = scored[0][0] / scored[1][0] if len(scored) > 1 else float("inf")
        _, name, shared = scored[0]
        page = self.pages[name]
        if ratio < _MARGIN or len(shared) < 2:
            return None
        anchor = any(_name_like(w) and self.adf[w] <= _ANCHOR_MAX_PAGES
                     for w in shared & page["anchors"])
        rare = sum(1 for w in shared if _name_like(w) and self.df[w] <= _RARE_MAX_PAGES)
        if anchor or rare >= 2 or (rare == 1 and ratio >= _MARGIN_ONE_RARE):
            return name
        return None


# ------------------------------------------------------------ 새 페이지와 타임라인 줄

def _ko(value) -> str:
    """한글이 든 글이면 공백 정리해 돌려주고, 아니면 빈 문자열."""
    s = " ".join(str(value or "").replace("**", "").split())
    return s if _HANGUL_RE.search(s) else ""


def _korean_fact(item: dict) -> str:
    """타임라인 한 줄에 쓸 한국어 사실. 영어 원제는 쓰지 않는다."""
    return _ko(item.get("title_ko")) or _first_sentence(_ko(item.get("summary_ko")))


def _fallback_slug(item: dict) -> str:
    words = re.findall(r"[a-z0-9]+", (item.get("title") or "").lower())
    words = [w for w in words if len(w) > 1][:6]
    if len(words) >= 2:
        return "-".join(words)[:60].strip("-")
    digest = hashlib.sha1((item.get("url") or item.get("id") or "").encode()).hexdigest()[:8]
    return f"event-{digest}"


def _timeline_line(item: dict, day: str, fact: str) -> str:
    source = (item.get("source") or "출처").replace("[", "").replace("]", "")
    return f"- {day} [{source}]({item.get('url', '')}) — {fact}"


def _page_text(slug: str, day: str, summary: str, line: str,
               tags: list[str], cves: list[str]) -> str:
    return (
        "---\n"
        f"slug: {slug}\n"
        f"first_seen: {day}\n"
        f"tags: [{', '.join(tags)}]\n"
        f"cves: [{', '.join(cves)}]\n"
        "---\n\n"
        f"{summary}\n\n"
        "## 타임라인\n\n"
        f"{line}\n\n"
        "## 관련\n"
    )


def _new_page(slug: str, item: dict, day: str, fact: str) -> str:
    text = " ".join(str(item.get(k) or "") for k in ("title", "summary", "title_ko", "summary_ko"))
    cves = sorted(dedup_lib.extract_cves(text))
    tags = normalize_tags([t for t in (item.get("tags_ko") or []) if isinstance(t, str)])[:4]
    summary = " ".join(str(item.get("summary_ko") or "").split())
    if not _HANGUL_RE.search(summary):
        summary = fact
    return _page_text(slug, day, summary, _timeline_line(item, day, fact), tags, cves)


def _create_page(files: dict[str, str], name: str, text: str) -> str:
    """새 페이지를 쓴다. 대소문자만 다른 파일이 이미 있으면 덮어쓰지 않고 그
    파일명을 돌려준다(Windows 덮어쓰기 재현 2026-11-20). 실제 파일명 반환."""
    path = os.path.join(TOPICS_DIR, f"{name}.md")
    try:
        with open(path, "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except FileExistsError:
        files.update(topic_files())
        return {n.lower(): n for n in files}.get(name.lower(), name)
    files[name] = path
    return name


# ------------------------------------------------------------ 검증

def ensure_recorded(items: list[dict], verdicts: dict | None, day: str,
                    *, sent: bool = False) -> dict:
    """항목의 위키 기록을 확인하고 없으면 보충한다. 집계 dict 반환.

    사서 한국어 문안(title_ko, summary_ko)을 항목에 병합한 뒤에 부른다.
    sent=False: 사서가 new나 update로 판정한 항목만 본다(사서 판정 기준).
    sent=True: 실제 발송한 뉴스 항목. 판정이 없거나 kind를 몰라도 기록한다.
    kind가 vuln이나 other로 확실한 항목만 뺀다.
    판정에 쓸 만한 topic이 없으면 기존 페이지를 찾아 붙이고, 없으면 새로 만든다.
    페이지 글은 한국어만 쓴다. 한국어 제목과 요약이 모두 없으면 건너뛴다."""
    files = topic_files()
    verdicts = verdicts if isinstance(verdicts, dict) else {}
    stats = {"checked": 0, "created": 0, "appended": 0, "skipped": 0, "links": 0}
    index: _PageIndex | None = None
    for item in items or []:
        if not isinstance(item, dict):
            continue
        v = verdicts.get(item.get("id"))
        v = v if isinstance(v, dict) else {}
        action = v.get("action") if isinstance(v.get("action"), str) else None
        kind = normalize_kind(item.get("kind")) or normalize_kind(v.get("kind"))
        if sent:
            if kind in ("vuln", "other"):
                continue
        elif action not in ("new", "update") or (kind is not None and kind not in WIKI_KINDS):
            continue
        stats["checked"] += 1
        url = item.get("url") or ""
        fact = _korean_fact(item)
        topic = v.get("topic") if isinstance(v.get("topic"), str) else ""
        slug = topic.strip().lower()
        name = None
        if _SLUG_RE.match(slug):
            name = find_topic(slug, files)
        else:
            if index is None:
                index = _PageIndex(files)
            name = index.match({**item, "date": day})
            slug = _strip_month(name) if name else _fallback_slug(item)
            if v is verdicts.get(item.get("id")):
                v["topic"] = slug
        if name is None:
            if not fact:
                stats["skipped"] += 1
                print(f"[wiki] 한국어 문안 없음, 기록 건너뜀: {url}", file=sys.stderr)
                continue
            name = f"{day[:7]}-{slug}"
            made = _create_page(files, name, _new_page(slug, item, day, fact))
            if made == name:
                stats["created"] += 1
                print(f"[wiki] 위키에 없던 페이지 보충 생성: {name}", file=sys.stderr)
                if index is not None:
                    index.update(name, _read(files[name]))
                continue
            name = made
        path = files.get(name)
        if path is None:
            stats["skipped"] += 1
            continue
        text = _read(path)
        if url and url not in text:
            if not fact:
                stats["skipped"] += 1
                print(f"[wiki] 한국어 문안 없음, 기록 건너뜀: {url}", file=sys.stderr)
                continue
            text = _insert_timeline(text, _timeline_line(item, day, fact))
            _write(path, text)
            stats["appended"] += 1
            if index is not None:
                index.update(name, text)
            print(f"[wiki] 위키에 없던 타임라인 줄 보충: {name}", file=sys.stderr)

    stats["links"] = migrate_links()
    print(f"[wiki] 기록 검증{'(발송분)' if sent else ''}: 확인 {stats['checked']}건, "
          f"페이지 보충 {stats['created']}건, 타임라인 보충 {stats['appended']}건, "
          f"건너뜀 {stats['skipped']}건, 링크 정리 {stats['links']}개 페이지",
          file=sys.stderr)
    return stats


# ------------------------------------------------------------ 원장 소급 기록

def _entry_source(entry: dict) -> str:
    if entry.get("source"):
        return str(entry["source"])
    host = (urlparse(entry.get("url") or "").hostname or "출처").lower()
    return host[4:] if host.startswith("www.") else host


def _entry_slug(entry: dict, files: dict[str, str]) -> str:
    """새 페이지 slug. URL 끝 경로의 영문 단어, 원제 영문 단어, 해시 순."""
    seg = [s for s in urlparse(entry.get("url") or "").path.split("/") if s]
    words = []
    if seg:
        last = re.sub(r"\.(html?|php|aspx?|jsp)$", "", seg[-1].lower())
        words = [w for w in re.findall(r"[a-z0-9]+", last) if len(w) > 1]
        if sum(1 for w in words if w.isalpha()) < 2 or len(words) < 3:
            words = []
    slug = "-".join(words[:6])[:60].strip("-")
    if not slug:
        for key in ("title", "title_ko"):
            # 숫자만인 낱말은 빼고 영문 낱말이 둘 이상일 때만(예: 'ai-90-820' 방지)
            alpha = [w for w in re.findall(r"[a-z0-9]+", str(entry.get(key) or "").lower())
                     if len(w) > 1 and not w.isdigit()]
            if len(alpha) >= 2:
                slug = "-".join(alpha[:6])[:60].strip("-")
                break
    if not slug or not _SLUG_RE.match(slug):
        slug = _fallback_slug({"url": entry.get("url") or entry.get("title_ko") or ""})
    if find_topic(slug, files):
        slug = f"{slug[:52]}-{hashlib.sha1((entry.get('url') or '').encode()).hexdigest()[:6]}"
    return slug


def backfill_from_ledger(ledger_entries) -> dict:
    """발행 원장의 뉴스 항목 중 어느 타임라인에도 URL이 없는 것을 위키에 기록한다.

    가장 잘 맞는 기존 페이지 타임라인에 한 줄을 넣고, 없으면 페이지를 만든다.
    글은 title_ko만 쓴다(영어 원제 금지). 한국어 제목이 없거나 kind가 vuln,
    other로 확실한 항목은 건너뛴다. 이미 기록된 URL은 건드리지 않아 멱등이다."""
    stats = {"backfill_appended": 0, "backfill_created": 0, "backfill_skipped": 0}
    news = [e for e in (ledger_entries or [])
            if isinstance(e, dict) and e.get("lane") == "news" and e.get("url")]
    if not news:
        return stats
    files = topic_files()
    recorded: set[str] = set()
    for path in files.values():
        recorded |= _timeline_urls(_read(path))
    todo = [e for e in news if _url_key(e["url"]) not in recorded]
    if not todo:
        return stats
    index = _PageIndex(files)
    for e in sorted(todo, key=lambda x: str(x.get("date") or "")):
        key = _url_key(e["url"])
        day = str(e.get("date") or "")[:10]
        fact = _ko(e.get("title_ko"))
        if key in recorded:
            continue
        if not _parse_date(day) or not fact or normalize_kind(e.get("kind")) in ("vuln", "other"):
            stats["backfill_skipped"] += 1
            continue
        line = f"- {day} [{_entry_source(e).replace('[', '').replace(']', '')}]({e['url']}) — {fact}"
        name = index.match(e)
        if name:
            text = _insert_timeline(_read(files[name]), line)
            _write(files[name], text)
            stats["backfill_appended"] += 1
        else:
            slug = _entry_slug(e, files)
            name = f"{day[:7]}-{slug}"
            summary = _first_sentence(_ko(e.get("summary_ko")))
            if not summary.endswith((".", "다")):
                summary = fact
            raw = e.get("cves")
            cves = sorted({c.upper() for c in raw if isinstance(c, str)
                           and re.fullmatch(r"CVE-\d{4}-\d{4,7}", c, re.I)}
                          if isinstance(raw, list) else set())
            made = _create_page(files, name, _page_text(slug, day, summary, line, [], cves))
            if made != name:
                text = _insert_timeline(_read(files[made]), line)
                _write(files[made], text)
                name = made
                stats["backfill_appended"] += 1
            else:
                stats["backfill_created"] += 1
            text = _read(files[name])
        index.update(name, text)
        recorded.add(key)
    print(f"[wiki] 원장 소급 기록: 타임라인 {stats['backfill_appended']}줄, "
          f"새 페이지 {stats['backfill_created']}개, 건너뜀 {stats['backfill_skipped']}건",
          file=sys.stderr)
    return stats


# ------------------------------------------------------------ 정비 진입점

def maintenance(ledger_entries=None) -> dict:
    """digest마다 사서 실행 전에 한 번 부르는 위키 정비. 단계별 집계 dict.

    순서: 중복 병합 → slug 충돌 분리 → 소문자화 → 원장 소급 기록 → 태그 정리
    → 링크 정리. 이름을 바꾸는 단계가 먼저 끝나야 소급 기록이 정본 페이지에
    붙고, 링크 정리가 바뀐 이름을 따라간다. 단계 하나가 실패해도 나머지는
    돈다(위키 문제가 아침 브리핑을 막으면 안 된다)."""
    stats: dict = {}

    def run(label, fn):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — 정비 실패는 digest를 막지 않는다
            print(f"[wiki] 정비 단계 실패(무시) {label}: {exc}", file=sys.stderr)
            return None

    stats["merged"] = run("병합", merge_duplicates) or 0
    stats["slug_split"] = run("slug 분리", rename_collisions) or 0
    stats["lowercased"] = run("소문자화", lowercase_names) or 0
    stats.update(run("원장 소급", lambda: backfill_from_ledger(ledger_entries)) or {})
    stats["tags_pages"] = run("태그", lambda: fix_tags(stats)) or 0
    stats["links_pages"] = run("링크", lambda: migrate_links(stats)) or 0
    print(f"[wiki] 정비: {stats}", file=sys.stderr)
    return stats


if __name__ == "__main__":
    # 수동 실행: python wiki_guard.py maintenance  (원장은 state/published.json)
    if sys.argv[1:] == ["maintenance"]:
        import published_ledger
        print(maintenance(published_ledger.load()))
    else:
        print("usage: python wiki_guard.py maintenance", file=sys.stderr)
        sys.exit(2)
