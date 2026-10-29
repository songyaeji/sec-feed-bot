---
slug: jupiter-x-core-wordpress-twitter-auth-bypass
first_seen: 2026-10-28
tags: [Jupiter X Core, WordPress, 소셜로그인, 인증우회]
cves: [CVE-2026-106013]
---

Jupiter X Core 4.61.0 이하 WordPress 플러그인의 Twitter/X 소셜 로그인 핸들러에서 OAuth 토큰 교환 후 클라이언트에 할당하지 않아, 사이트 관리자의 저장된 토큰으로 API 요청이 계속 서명된다. CVSS 9.8으로 미인증 공격자가 사이트 관리자의 X 프로필로 검증되어 WordPress 슈퍼유저 계정을 탈취할 수 있다.

## 타임라인

- 2026-10-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-106013) — CVE-2026-106013 공개 (CVSS 9.8), Twitter OAuth 토큰 미할당

## 관련
