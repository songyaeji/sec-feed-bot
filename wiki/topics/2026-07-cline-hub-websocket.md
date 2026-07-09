---
slug: cline-hub-websocket
first_seen: 2026-07-08
tags: [AI코딩도구, WebSocket, CORS우회]
cves: [CVE-2026-59723]
---

AI 코딩 에이전트 **Cline** 3.0.30 이전 버전의 Hub 대시보드 서버가 `/browser` WebSocket 엔드포인트에서 Origin 헤더 검증 없이 연결 수락. ROOM_SECRET 미설정 시 로컬 공격자가 임의 사용자로 명령 실행 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59723) — CVE-2026-59723 (CVSS 8.8) WebSocket Origin 검증 부재
