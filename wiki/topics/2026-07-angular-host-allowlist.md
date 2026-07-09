---
slug: angular-host-allowlist
first_seen: 2026-06-22
tags: [Angular, 호스트검증우회, SSR]
cves: [CVE-2026-50168]
---

**Angular** 22.0.0-rc.2, 21.2.15, 20.3.22, 19.2.23 이전 버전의 `@angular/platform-server` 패키지에서 호스트 allowlist 제한을 우회할 수 있는 취약점. 서버 사이드 렌더링(SSR) 기능의 보안 검증 부실로 인한 것.

## 타임라인

- 2026-06-22 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-50168) — CVE-2026-50168 (CVSS 8.2) 호스트 allowlist 우회
