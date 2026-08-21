---
slug: microsoft-defender-btr-weaponization
first_seen: 2026-08-21
tags: [커널권한상향, 부팅시간공격, 정규드라이버악용, Windows보안]
cves: []
---

Check Point 연구팀이 **Microsoft Defender**의 정규 부팅 복구 드라이버인 **BTR.sys**(Boot Time Removal Tool)를 악용하는 공격 기법을 공개했다. 실제 소프트웨어 결함 없이 정규 서명된 드라이버를 활용해 Windows 7부터 Windows 11(25H2)까지 임의의 커널 수준 파일과 레지스트리 조작을 수행할 수 있다. 보안 소프트웨어 무력화의 새로운 경로로 평가된다.

## 타임라인

- 2026-08-21 [The Hacker News](https://thehackernews.com/2026/08/microsoft-defenders-own-driver-can-be.html) — Check Point Research BTR.sys 정규드라이버 악용 커널 권한 조작 기법 공개
