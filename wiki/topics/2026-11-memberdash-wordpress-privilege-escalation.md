---
slug: memberdash-wordpress-privilege-escalation
first_seen: 2026-11-14
tags: [WordPress플러그인, 권한상향, 회원정보변조]
cves: [CVE-2026-18053]
---

# MemberDash WordPress — 회원정보 변조 관리자 탈취

WordPress 플러그인 **MemberDash** 1.8.7 이하에서 user_account_manager() 함수의 프로필 편집 기능의 mass-assignment 취약점(CVSS 8.8). Subscriber 권한 이상 인증 사용자가 제출된 $_POST 필드를 모두 현재 사용자 객체에 직접 할당할 수 있고, id 파라미터 검증 부재로 임의 사용자 ID를 지정하여 타사용자의 이메일·비밀번호를 변조하고 관리자 권한 탈취 가능.

## 타임라인

- 2026-11-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-18053) — CVE-2026-18053 mass-assignment CVSS 8.8 권한 상향
