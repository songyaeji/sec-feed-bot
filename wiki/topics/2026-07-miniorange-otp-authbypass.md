---
slug: miniorange-otp-authbypass
first_seen: 2026-07-09
tags: [WordPress, 플러그인, 인증우회, 관리자탈취]
cves: [CVE-2026-14245]
---

# miniOrange OTP 플러그인 인증 우회 및 관리자 계정 탈취

WordPress 다중인증 플러그인 **miniOrange OTP Login, Verification and SMS Notifications** 버전 5.5.1 이하에서 발견된 극심 취약점. `um_reset_password_process_hook()` 함수가 비밀번호 재설정 과정에서 서버 측 검증을 수행하지 않아, 공격자가 임의 계정의 비밀번호를 재설정하고 관리자 권한을 탈취 가능(CVSS 9.8).

## 타임라인

- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14245) — CVE-2026-14245: miniOrange OTP 5.5.1 인증 우회 및 관리자 계정 탈취
