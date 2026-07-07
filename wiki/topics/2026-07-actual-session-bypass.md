---
slug: actual-session-bypass
first_seen: 2026-07-07
tags: [session management, OpenID, multi-user]
cves: [CVE-2026-49229]
---

**Actual** 개인 금융 관리 앱의 OpenID 다중 사용자 모드에서 세션 토큰 검증 우회 취약점. 사용자 비활성화 시 향후 OpenID 로그인만 차단되며, 기존 세션 토큰은 여전히 유효하여 비활성화된 사용자의 토큰 재사용 공격 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-49229) — CVE-2026-49229 공개 (CVSS 8.3)
