---
slug: rapisafe-wordpress-file-deletion
first_seen: 2026-08-15
tags: [WordPress, 파일삭제, 플러그인, 경로검증우회]
cves: [CVE-2026-14484]
---

RapiSafe – Secure Multi File Upload for Contact Form 7 WordPress 플러그인 1.0.4 이하에서 handleAjaxRemoveUpload 함수의 파일 경로 검증이 불충분하여, Contact Form 7 페이지에 공개적으로 노출된 RSMFCF7Vars.nonce를 이용해 미인증 사용자가 wp-config.php 같은 임의 서버 파일 삭제 및 원격코드 실행 가능. CVSS 9.1.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14484) — CVE-2026-14484 공개, 경로검증 우회로 인한 임의 파일 삭제 취약점 확인
