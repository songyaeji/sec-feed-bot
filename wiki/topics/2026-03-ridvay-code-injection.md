---
slug: ridvay-code-injection
first_seen: 2026-03-31
tags: [AI에이전트, 명령자동실행, 우회공격]
cves: [CVE-2026-30311, CVE-2026-30314]
---

# Ridvay Code 명령 자동 승인 쉘 메타문자 우회

Ridvay Code의 명령 자동 승인 모듈이 정규식 기반 명령 구조 파싱에서 표준 쉘 명령 치환($(...), 백틱)을 감지 불가해 악의적 명령을 안전한 git 연산으로 위장해 사용자 승인 우회 가능.

## 타임라인

- 2026-03-31 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-30311) — CVE-2026-30311 공개 (CVSS 9.8)
- 2026-03-31 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-30314) — CVE-2026-30314 공개 (동일 취약점, CVSS 9.8)

## 관련

없음
