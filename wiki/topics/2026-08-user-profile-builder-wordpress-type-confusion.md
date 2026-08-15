---
slug: user-profile-builder-wordpress-type-confusion
first_seen: 2026-08-15
tags: [WordPress, 타입컨퓨전, 플러그인, 권한탈취]
cves: [CVE-2026-15826]
---

User Profile Builder WordPress 플러그인 3.16.4 이하에서 wppb_log_in_user() 함수가 wp_insert_user() 반환값에 absint() 캐스팅을 하기 전에 WP_Error 체크를 누락, 61~70자 길이 사용자명 등록 시 WP_Error 객체가 정수 1로 강제 변환되어 관리자 계정(UID 1) 자동 로그인 토큰 발급으로 사이트 관리자 장악 가능. CVSS 9.8.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15826) — CVE-2026-15826 공개, 타입 컨퓨전으로 인한 관리자 계정 탈취 취약점 확인
