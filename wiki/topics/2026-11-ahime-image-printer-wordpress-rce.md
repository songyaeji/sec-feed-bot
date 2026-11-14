---
slug: ahime-image-printer-wordpress-rce
first_seen: 2026-11-13
tags: [원격코드실행, 파일업로드, 워드프레스플러그인, 미인증공격]
cves: [CVE-2026-124833]
---

**Ahime Image Printer** WordPress 플러그인 1.0.0 이하에서 업로드 파일의 이름·확장자·타입을 검증하지 않아 미인증 공격자가 PHP 파일을 포함한 임의 파일을 서버에 업로드해 원격 코드 실행 가능.

## 타임라인

- 2026-11-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-124833) — CVE-2026-124833 Ahime Image Printer 플러그인 파일검증 부재 원격코드실행 (CVSS 9.8)

## 관련

[[advance-guest-post-wordpress-rce]]
