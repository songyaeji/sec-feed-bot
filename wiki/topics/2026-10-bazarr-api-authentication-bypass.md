---
slug: bazarr-api-authentication-bypass
first_seen: 2026-10-30
tags: [미인증API변조, 인증우회, 자막관리플랫폼]
cves: [CVE-2026-61826]
---

Bazarr는 Sonarr·Radarr의 companion 애플리케이션으로, Plex 통합을 처리하는 API 네임스페이스에서 인증을 생략해 미인증 사용자가 Plex 설정을 변조하거나 자격증명을 탈취할 수 있다.

## 타임라인

- 2026-10-30 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-61826) — Plex OAuth API 미인증 변조로 서버 설정 조작·토큰 탈취·SSRF 공격 가능, 버전 1.5.7-beta.14 이상에서 패치

## 관련

없음
