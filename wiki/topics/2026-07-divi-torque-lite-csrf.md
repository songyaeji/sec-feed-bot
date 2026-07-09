---
slug: divi-torque-lite-csrf
first_seen: 2026-07-09
tags: [WordPress, 플러그인, CSRF, 인증]
cves: [CVE-2026-4275]
---

# Divi Torque Lite 플러그인 CSRF 인증 우회

WordPress 페이지 빌더 플러그인 **Divi Torque Lite** (Divi Theme, Divi Builder & Extra Theme) 4.2.3 이하 버전에서 `/install_plugin` 및 `/activate_plugin` REST API 엔드포인트가 `__return_true`를 권한 검증 콜백으로 사용하여 CSRF 공격으로 미인증 사용자가 플러그인 설치/활성화 가능(CVSS 8.8).

## 타임라인

- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-4275) — CVE-2026-4275: Divi Torque Lite 4.2.3 CSRF 플러그인 설치/활성화
