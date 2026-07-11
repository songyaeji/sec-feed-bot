---
slug: blocksy-companion-rce
first_seen: 2026-07-08
tags: [WordPress, 파일업로드, RCE]
cves: [CVE-2026-58480, CVE-2026-15158]
---

WordPress 플러그인 **Blocksy Companion Pro** 2.1.47 이전의 Advanced Reviews 기능에서 파일 확장자 검증을 우회한 **미인증 파일 업로드** 취약점. 공격자가 PHP 등 실행 가능한 파일을 업로드해 **원격 코드 실행**이 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-58480) — CVE-2026-58480: 미인증 파일 업로드 RCE (CVSS 9.8)
- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15158) — CVE-2026-15158: Custom Fonts extension 파일 확장자 검증 우회 (2.1.46 이전, CVSS 9.8)

## 관련
