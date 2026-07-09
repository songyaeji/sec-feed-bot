---
slug: divi-form-builder-authbypass
first_seen: 2026-07-09
tags: [WordPress, 플러그인, 미인증권한, 계정조작]
cves: [CVE-2026-5523]
---

# Divi Form Builder 플러그인 미인증 사용자 권한 취약점

WordPress 인기 페이지 빌더 플러그인 **Divi Form Builder** 버전 5.1.8 이하에서 발견된 중대 취약점. 폼 제출 중 `update_user()` 함수가 사용자 ID 매개변수를 서버 측 권한 검증 없이 수용하여, 미인증 공격자가 다른 사용자 계정(관리자 포함) 정보를 임의로 변경 가능(CVSS 8.8).

## 타임라인

- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-5523) — CVE-2026-5523: Divi Form Builder 5.1.8 미인증 사용자 정보 변경
