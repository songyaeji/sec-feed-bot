---
slug: openam-websocket-token-leak
first_seen: 2026-11-08
tags: [인증우회, 세션탈취, SSO, CVE-2026-123551]
cves: [CVE-2026-123551]
---

**OpenAM** 인증 플랫폼의 알림 WebSocket 채널에서 미인증 공격자가 실시간으로 유효한 세션 토큰을 읽을 수 있는 정보 유출 취약점이 발견되었다. 리거시 Liberty ID-FF 엔드포인트의 검증 우회를 통해 iPlanetDirectoryPro 토큰을 수집해 사용자·관리자 세션을 탈취할 수 있으며, SSO 인프라 전체 침해로 확산 가능하다.

## 타임라인

- 2026-11-08 [NVD CVE-2026-123551](https://nvd.nist.gov/vuln/detail/CVE-2026-123551) — OpenAM 14.0.0~16.1.4 WebSocket 알림 채널 세션 토큰 정보 유출 CVSS 10.0
