---
slug: note-mark-jwt-weak-secret
first_seen: 2026-05-14
tags: [OpenSource, JWT, 약한검증, 인증우회]
cves: [CVE-2026-44523]
---

오픈소스 노트 애플리케이션 Note Mark v0.19.4 이전에서 JWT_SECRET 최소 길이 및 엔트로피 미검증. 1바이트 길이 비밀값 포함 base64 디코드 가능한 모든 값 허용으로 JWT 서명 위조 가능.

## 타임라인

- 2026-05-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44523) — CVE-2026-44523 공개 (CVSS 10.0, v0.19.4에서 패치)
