---
slug: sleepwalker-backdoor
first_seen: 2026-08-26
tags: [백도어, 탐지우회, DLL-Sideloading]
cves: []
---

독립 악성코드 연구자가 **SLEEPWALKER** Windows 백도어를 공개했다. 59,904바이트 unsigned 64-bit DLL이 side-loading으로 주입되어 메모리에서 정상 동작을 위장하다가, 특정 형식의 네트워크 패킷을 수신하면 23개 명령어로 된 커스텀 바이트코드 언어로 임의 명령을 실행한다. 탐지 회피 설계에 중점.

## 타임라인

- 2026-08-26 [The Hacker News](https://thehackernews.com/2026/08/newly-sleepwalker-backdoor-waits-for.html) — SLEEPWALKER 백도어 분석, 네트워크 신호 기반 활성화

## 관련
