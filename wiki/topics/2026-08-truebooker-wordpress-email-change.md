---
slug: truebooker-wordpress-email-change
first_seen: 2026-08-15
tags: [WordPress, 인증우회, 플러그인, 계정탈취]
cves: [CVE-2026-16142]
---

TrueBooker WordPress 플러그인 1.2.6 이하에서 add_front_user_update() AJAX 핸들러가 미인증 사용자 요청을 수락하고 truebooker_wp_user_id 파라미터를 검증 없이 wp_update_user()에 전달하여, 임의 사용자(관리자 포함)의 이메일 주소 변경이 가능. 공격자가 변조된 이메일로 기본 WordPress 비밀번호 재설정 흐름을 통해 계정 장악. CVSS 9.8.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16142) — CVE-2026-16142 공개, 이메일 변경을 통한 계정 탈취 취약점 확인
