---
slug: rucio-ssh-challenge-auth-bypass
first_seen: 2026-11-17
tags: [인증우회, 계정탈취, API보안]
cves: [CVE-2026-100397]
---

과학 데이터 관리 프레임워크 **Rucio**의 인증 모듈이 SSH 챌린지 토큰을 인증 토큰과 구분 불가. CVSS 10.0으로 완전 계정 탈취 가능하며 관리자 권한도 대상.

## 타임라인

- 2026-11-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-100397) — CVE-2026-100397 Rucio 1.14.0~41.1.1 SSH 챌린지 토큰 미검증 인증 우회 CVSS 10.0

## 관련

- [[api-security-vulnerabilities]]
