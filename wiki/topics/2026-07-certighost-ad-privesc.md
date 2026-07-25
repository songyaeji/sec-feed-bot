---
slug: certighost-ad-privesc
first_seen: 2026-07-24
tags: [권한상향, ActiveDirectory, 인증서악용]
cves: []
---

낮은 권한의 Active Directory 사용자가 도메인 컨트롤러용 인증서를 획득해 DC로 인증하고 DCSync 권한으로 krbtgt 해시를 탈취할 수 있는 취약점 Certighost. 권한상향의 새로운 입입로 확보.

## 타임라인

- 2026-07-24 [The Hacker News](https://thehackernews.com/2026/07/certighost-exploit-lets-low-privileged.html) — 보안 연구자 H0j3n·Aniq Fakhrul, Certighost 익스플로잇 공개

## 관련

- [[ad-security]]
- [[privilege-escalation]]
