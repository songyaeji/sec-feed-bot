---
slug: shipo-wordpress-auth-bypass
first_seen: 2026-11-14
tags: [WordPress플러그인, 인증우회, 관리자탈취]
cves: [CVE-2026-19907]
---

# Shipo WordPress — REST API 미인증 관리자 탈취

WordPress 플러그인 **Shipo** 1.6~1.8.0의 authenticate_rest_user() 함수가 LOGGED_IN_COOKIE 값에서 사용자를 파싱하지만 쿠키의 암호화 서명을 검증하지 않음(CVSS 9.8). 또한 /wp-json/shipo/ 경로 제한을 쿼리 스트링에 포함시켜 우회 가능. 미인증 공격자가 기존 사용자명으로 위조 쿠키를 제작하여 REST API에 접근하고 관리자 계정 생성 등 권한된 조치 수행 가능.

## 타임라인

- 2026-11-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-19907) — CVE-2026-19907 쿠키 서명 미검증 CVSS 9.8 REST API 인증 우회
