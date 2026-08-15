---
slug: propovoice-wordpress-role-creation
first_seen: 2026-08-15
tags: [WordPress, 권한상향, 플러그인, 계정생성]
cves: [CVE-2026-15312]
---

Propovoice: All-in-One Client Management System WordPress 플러그인 1.7.8 이하에서 create() 함수의 REST 엔드포인트가 user-supplied role 파라미터를 허용된 역할 목록에 대조하지 않고 promote_users 권한 검사도 누락하여, ndpv_manager(서브관리자 CRM 역할) 권한 사용자가 administrator 역할 신규 관리자 계정 생성 및 수직 권한상향 가능. CVSS 8.8.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15312) — CVE-2026-15312 공개, 역할 검증 우회로 인한 관리자 계정 생성 취약점 확인
