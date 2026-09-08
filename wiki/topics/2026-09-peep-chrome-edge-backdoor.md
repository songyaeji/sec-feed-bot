---
slug: peep-chrome-edge-backdoor
first_seen: 2026-09-07
tags: [백도어, 브라우저악용, 후킹, 원격코드실행]
cves: []
---

정교한 Chromium 기반 후익스플로잇 도구킷인 **PEEP**이 발견되었다. 관리자 권한이나 코드 실행 접근이 필요하며, **북마크 확장으로 위장하여 Chrome/Edge 프로필에 직접 주입**되어 Web Store 검증과 사용자 프롬프트를 우회한다. Chromium의 Secure Preferences 위조를 통해 확장이 설치됨을 숨긴다.

## 타임라인

- 2026-09-07 [The Hacker News](https://thehackernews.com/2026/09/peep-turns-chrome-and-edge-into-post.html) — PEEP 도구킷 분석 보고서 공개, Chrome/Edge 선택적 주입, 북마크 확장 위장, 호스트 명령 실행

## 관련
