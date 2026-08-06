---
slug: jwt-auth-algorithm-confusion
first_seen: 2026-08-06
tags: [JWT, 인증우회, RCE]
cves: [CVE-2026-5430]
---

# JWT 인증 알고리즘 혼동 - 원격코드실행

**CVE-2026-5430** JWT 인증 메커니즘이 명시적으로 구성된 알고리즘 이외의 다른 알고리즘 서명을 수용하는 취약점. 공격자가 지원되지 않은 알고리즘으로 JWT를 조작하면 검증 단계를 우회해 관리자 계정까지 탈취 가능. **CVSS 10.0** 중대 취약점이며 관리자 권한 탈취 및 전체 시스템 침해 위험.

## 타임라인

- 2026-08-06 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-5430) — CVE-2026-5430 공개 (CVSS 10.0)
