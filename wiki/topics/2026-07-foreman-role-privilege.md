---
slug: foreman-role-privilege
first_seen: 2026-07-01
tags: [권한상향, 접근제어, 역할관리]
cves: [CVE-2026-5136]
---

# Foreman 자산 관리 시스템 역할 권한 검증 부재

인프라 자동화·관리 플랫폼 Foreman에서 발견된 권한상향 취약점. **Usergroup** 모델이 사용자 권한 검증을 실패하여 usergroup 관리 권한을 보유한 인증된 사용자가 임의의 역할(관리자 포함)을 사용자 그룹에 부여 가능(CVSS 8.8).

## 타임라인

- 2026-07-01 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-5136) — CVE-2026-5136: Foreman Usergroup 모델 역할 검증 부재
