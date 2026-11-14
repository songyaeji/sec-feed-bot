---
slug: automatorwp-pro-auth-bypass
first_seen: 2026-11-14
tags: [WordPress플러그인, 인증우회, 계정탈취]
cves: [CVE-2026-126173]
---

# AutomatorWP Pro — 미인증 비밀번호 리셋

WordPress 플러그인 **AutomatorWP Pro** 1.4.4 이하의 webhook 애드온에서 사용자 인증 검증 미흡(CVSS 9.8). 특정 워크플로우 설정(Receive Webhook 트리거 + Update-User 액션)에서 미인증 공격자가 webhook 요청으로 임의 계정의 비밀번호를 리셋하여 관리자 권한 탈취 가능.

## 타임라인

- 2026-11-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-126173) — CVE-2026-126173 webhook 인증 검증 우회 CVSS 9.8 어드민 계정 탈취
