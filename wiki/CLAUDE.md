# wiki/ 사서 규약

이 디렉터리는 `librarian.py`가 digest 모드에서 자동으로 관리하는 보안동향
위키다. 사람이 손으로 편집해도 되지만, 이 규약을 지켜야 자동화가 계속
작동한다.

## 범위

- **`wiki/topics/*.md` 밖의 파일을 만들거나 수정하지 않는다.** 이 규약을
  읽는 주체(사서 role의 Claude)는 토픽 페이지만 쓰고 고친다. `wiki/INDEX.md`는
  읽기만 한다. 저장소의 다른 파일(main.py, state/, config.yaml 등)은 절대
  건드리지 않는다. 실행 중 새로 생긴 규약 밖 파일은 코드(wiki_guard)가 지운다.
- 위키의 역할은 사건 기록 보관이다. 카드뉴스의 날짜를 넘는 중복 판정은
  위키가 아니라 발행 원장(`state/published.json`)이 맡는다(2026-11-20).

## 토픽 페이지

- 경로: `wiki/topics/YYYY-MM-topic-slug.md` (YYYY-MM은 사건을 처음 인지한
  달, slug는 영문 소문자·숫자·하이픈으로 사건을 짧게 표현).
- frontmatter:
  ```yaml
  ---
  slug: topic-slug
  first_seen: YYYY-MM-DD
  tags: [태그1, 태그2]
  cves: [CVE-YYYY-NNNNN]
  ---
  ```
- 본문 구조:
  1. 3줄 이내 요약 (사건이 무엇인지, 왜 중요한지).
  2. `## 타임라인` — 시간순으로 한 줄씩:
     `- YYYY-MM-DD [출처명](url) — 새 사실 한 줄`
     같은 사건에 대한 새 기사가 들어올 때마다 여기 한 줄을 추가한다.
     기존 사실의 반복이면 새 줄을 추가하지 않는다(=`skip_duplicate`).
  3. `## 관련` — 연관 토픽이 있으면 `[[YYYY-MM-topic-slug]]`처럼 확장자 없는
     **파일명**으로 링크한다. Obsidian은 파일명으로만 링크를 연다.
- 사서가 new·update로 판정한 항목은 반드시 페이지와 타임라인 줄을 남긴다.
  빠지면 코드(wiki_guard.ensure_recorded)가 최소 페이지·줄을 보충한다.

## INDEX.md

- `INDEX.md`와 `INDEX-archive.md`는 코드(wiki_index.rebuild_index)가 토픽
  페이지에서 매 digest마다 다시 만든다. 사서는 고치지 않는다.
- `INDEX.md`에는 최근(약 60일) 갱신 토픽만, 그보다 오래된 것은
  `INDEX-archive.md`에 실린다. 옛 사건과의 중복 여부가 의심되면
  `wiki/topics/`를 Grep으로 확인한다.

## 위키에 넣지 않는 것

- 토픽 페이지는 사고(`incident`)·법제도(`policy`)·기관 발표(`institution`)만
  만든다. 단순 취약점 공개·패치·권고(`vuln`)와 홍보·실적·행사·칼럼(`other`)은
  페이지를 만들지 않는다 (verdict: `no_wiki`). 취약점 기사는 카드뉴스의
  '오늘의 CVE' 코너로만 간다.
