---
slug: bitwarden-admin-request-privesc
first_seen: 2026-07-08
tags: [권한상향, 인증우회]
cves: [CVE-2026-60104]
---

Bitwarden Server 2026.6.0 이전 버전의 `/auth-requests/admin-request` API에서 요청자 이메일 검증이 누락돼 낮은 권한의 조직원이 다른 사용자의 vault key와 access token을 탈취할 수 있다. 조직 내 비밀 정보 접근 권한이 상향된다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-60104) — CVE-2026-60104 (CVSS 8.7) 공개

## 관련

