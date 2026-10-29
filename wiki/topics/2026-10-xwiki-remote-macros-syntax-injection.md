---
slug: xwiki-remote-macros-syntax-injection
first_seen: 2026-10-28
tags: [XWiki, 위키플랫폼, 원격코드실행, 문법인젝션]
cves: [CVE-2026-44179]
---

XWiki Remote Macros 1.13~1.14.5 버전에서 `excerpt-include` 매크로가 포함 페이지 제목과 내용을 제대로 이스케이프하지 않아, 문서 편집 권한만으로도 매크로 문법 인젝션으로 임의 코드를 실행할 수 있다. CVSS 9.9로 프로그래밍 권한이 없어도 악용 가능해 설치 전역의 기밀성·무결성·가용성에 영향을 줄 수 있다.

## 타임라인

- 2026-10-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44179) — CVE-2026-44179 공개 (CVSS 9.9), excerpt-include 매크로 문법 인젝션

## 관련
