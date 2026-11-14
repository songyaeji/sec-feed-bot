---
slug: advance-guest-post-wordpress-rce
first_seen: 2026-11-13
tags: [원격코드실행, 파일업로드, 워드프레스플러그인, 미인증공격]
cves: [CVE-2026-118063, CVE-2026-118064]
---

**Advance Guest Post** WordPress 플러그인 1.9 이하에서 2개의 파일업로드 취약점으로 미인증 공격자가 임의 PHP 파일을 웹 접근 디렉터리에 업로드해 원격 코드 실행. ① CVE-2026-118063: 대소문자 구분·미흡한 확장자 검사로 .php 변형(.pHP 등) 우회 가능, ② CVE-2026-118064: 모든 방문자에 노출된 nonce와 레딩 바이트만 검사로 우회 (PHP 7.x 한정, PHP 8.0+는 fatal error).

## 타임라인

- 2026-11-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-118063) — CVE-2026-118063 Advance Guest Post 확장자 검증 우회 파일업로드 RCE (CVSS 9.8)
- 2026-11-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-118064) — CVE-2026-118064 Advance Guest Post nonce 노출 파일업로드 RCE (CVSS 9.8)

## 관련
