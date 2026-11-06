---
slug: avtech-eagleeyes-ssl-bypass
first_seen: 2025-09-15
tags: [HTTPS, 중간자공격, SSL우회]
cves: [CVE-2025-46408]
---

**AVTECH EagleEyes 2.0.0**의 Push 라이브러리 `GetHttpsResponse`, `getNewHttpClient` 메소드가 **HTTPS 호스트명 검증을 무시하도록 설정**(`ALLOW_ALL_HOSTNAME_VERIFIER`)하여 **중간자 공격(MITM)** 위험 (CVSS 9.8).

## 타임라인

- 2025-09-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-46408) — CVE-2025-46408 공개 (CVSS 9.8)

## 관련
