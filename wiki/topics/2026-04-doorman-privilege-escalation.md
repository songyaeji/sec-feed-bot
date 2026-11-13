---
slug: doorman-privilege-escalation
first_seen: 2026-04-20
tags: [접근제어, 권한상향, 자가권한상향, 플랫폼관리]
cves: [CVE-2026-30269]
---

# Doorman — 인증된 사용자 자가 권한상향 취약점

Doorman v0.1.0과 v1.0.2에서 부적절한 접근제어 취약점이 존재한다. 인증된 모든 사용자가 /platform/user/{username} 엔드포인트를 통해 자신의 계정 role을 비관리자 권한 역할로 업데이트할 수 있다. update 모델이 자기 자신 업데이트 시 manage_users 권한 검증을 하지 않아 고권한 역할로의 권한상향이 가능하다.

## 타임라인

- 2026-04-20 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-30269) — CVE-2026-30269 공개, CVSS 9.9

## 관련
