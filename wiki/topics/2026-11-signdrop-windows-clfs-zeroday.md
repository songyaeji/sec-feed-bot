---
slug: signdrop-windows-clfs-zeroday
first_seen: 2026-11-12
tags: [제로데이, Windows, 권한상향, CLFS]
cves: []
---

Windows Common Log File System(CLFS) 드라이버의 보안 기능을 악용해 권한을 **SYSTEM**으로 상향하는 제로데이 익스플로잇 **SignDrop**이 공개됐다. 지난해 추가된 로그 인증 기능의 설계 결함을 이용해 경로 리다이렉션으로 동반 파일 제어권을 탈취한다.

## 타임라인

- 2026-11-12 [The Hacker News](https://thehackernews.com/2026/11/new-signdrop-zero-day-exploit-turns.html) — SignDrop 제로데이 익스플로잇 공개, PoC 코드 일반 공개
- 2026-11-12 [BleepingComputer](https://www.bleepingcomputer.com/news/security/new-windows-signdrop-zero-day-gives-hackers-system-privileges/) — SignDrop 제로데이 활발히 악용 중

## 관련

