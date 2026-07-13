# wiki/ 사서 규약

이 디렉터리는 `librarian.py`가 digest 모드에서 자동으로 관리하는 보안동향
위키다. 사람이 손으로 편집해도 되지만, 이 규약을 지켜야 자동화가 계속
작동한다.

## 범위

- **wiki/ 밖의 파일을 수정하지 않는다.** 이 규약을 읽는 주체(사서 role의
  Claude)는 `wiki/INDEX.md`, `wiki/topics/*.md`만 쓰고 고친다. 저장소의
  다른 파일(main.py, state/, config.yaml 등)은 절대 건드리지 않는다.

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
  3. `## 관련` — 연관 토픽이 있으면 `[[slug]]` 형식으로 링크.

## INDEX.md 갱신 의무

- 새 토픽 페이지를 만들면 `wiki/INDEX.md`에 반드시 한 줄을 추가한다:
  `- [slug](topics/slug.md) 한줄요약 (최종갱신일: YYYY-MM-DD)`
- 기존 토픽 페이지에 타임라인을 추가했다면 INDEX.md의 해당 줄도 한줄요약과
  최종갱신일을 최신 상태로 갱신한다.
- `INDEX.md`에는 최근(약 60일) 갱신 토픽만 남는다 — 더 오래된 줄은
  자동화(main.py)가 `INDEX-archive.md`로 옮긴다. 옛 사건과의 중복 여부가
  의심되면 `wiki/topics/`·`INDEX-archive.md`를 Grep으로 확인해도 된다.
  아카이브 파일은 손으로 갱신할 의무가 없다.

## 위키에 넣지 않는 것

- 단순 나열성 기사(제품 홍보, 컨퍼런스 안내, 채용 등 사건성이 없는 글)는
  토픽 페이지를 만들지 않는다 (verdict: `no_wiki`).
