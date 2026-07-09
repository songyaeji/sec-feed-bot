---
slug: passgate-ldap-injection
first_seen: 2026-07-09
tags: [PassGate, LDAP인젝션, 접근제어우회]
cves: [CVE-2026-4256]
---

PEAKUP Technology의 **PassGate** 접근제어 솔루션에서 LDAP 쿼리 생성 시 특수문자 중립화 부재로 LDAP 인젝션 가능. 30042026 버전 이전에서 인증 우회 및 권한상향 공격 가능성.

## 타임라인

- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-4256) — CVE-2026-4256 (CVSS 8.2) LDAP 인젝션
