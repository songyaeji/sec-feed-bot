---
slug: adobe-connect-critical-flaws
first_seen: 2026-11-10
tags: [Adobe Connect, 화상회의, 다중취약점]
cves: [CVE-2026-121351, CVE-2026-121352, CVE-2026-121353, CVE-2026-121356, CVE-2026-121889]
---

**Adobe Connect** 화상회의 플랫폼에서 5개의 CVSS 10.0 치명적 취약점이 동시 발견됐다. 경로 순회로 임의 파일 시스템 읽기, 부적절한 권한 검증으로 권한 상升, CRLF 인젝션으로 임의 코드 실행, SSRF로 권한 상升이 모두 인증 필요 없이 가능하다.

## 타임라인

- 2026-11-10 [NVD CVE-2026-121351](https://nvd.nist.gov/vuln/detail/CVE-2026-121351) — 경로 순회 취약점 (Path Traversal) CVSS 10.0
- 2026-11-10 [NVD CVE-2026-121352](https://nvd.nist.gov/vuln/detail/CVE-2026-121352) — 권한 상升 취약점 (Incorrect Authorization) CVSS 10.0
- 2026-11-10 [NVD CVE-2026-121353](https://nvd.nist.gov/vuln/detail/CVE-2026-121353) — CRLF 인젝션 (CRLF Injection) CVSS 10.0 임의 코드 실행 가능
- 2026-11-10 [NVD CVE-2026-121356](https://nvd.nist.gov/vuln/detail/CVE-2026-121356) — SSRF 취약점 (Server-Side Request Forgery) CVSS 10.0
- 2026-11-10 [NVD CVE-2026-121889](https://nvd.nist.gov/vuln/detail/CVE-2026-121889) — SSRF 취약점 (Server-Side Request Forgery) CVSS 10.0
