---
slug: prosolution-wordpress-file-deletion
first_seen: 2026-08-16
tags: [WordPress, 파일삭제, RCE, 플러그인취약점]
cves: [CVE-2026-14524]
---

# ProSolution WordPress — 경로검증 우회 파일 삭제·RCE

**ProSolution WP Client** 플러그인 2.0.8 이하의 proSol_fileDeleteProcess 함수가 파일 경로를 충분히 검증하지 않아, 미인증 공격자가 먼저 proSol_fileUploadModalProcess로 세션에 경로 조작 키를 주입한 후 파일 삭제 API를 호출하여 wp-config.php 같은 임의 파일 삭제 및 원격코드 실행 가능.

## 타임라인

- 2026-08-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14524) — CVE-2026-14524 CVSS 9.1 공개, 경로검증 우회로 인한 조건부 RCE 확인

## 관련

[[link-library-wordpress-file-deletion]] — Link Library WordPress 플러그인 경로검증 우회 파일 삭제
