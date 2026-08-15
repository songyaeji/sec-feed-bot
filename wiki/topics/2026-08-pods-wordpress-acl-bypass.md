---
slug: pods-wordpress-acl-bypass
first_seen: 2026-08-15
tags: [WordPress, 권한상향, 플러그인, 접근제어우회]
cves: [CVE-2026-19598]
---

Pods – Custom Content Types and Fields WordPress 플러그인 3.3.9 이하에서 pods_admin AJAX 라우터의 모든 접근제어(허용 목록, nonce 검증, 로그인 강제, 권한 체크)가 pods_error() 함수를 거쳐 실패 시 단순히 에러 로그 작성만 하고 요청을 계속 처리, 미인증 사용자가 관리자 권한 획득 또는 사이트 소유자 비밀번호 변경으로 완전 제어 가능. CVSS 9.8.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-19598) — CVE-2026-19598 공개, 접근제어 완전 우회로 인한 권한상향 취약점 확인
