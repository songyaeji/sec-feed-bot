---
slug: qpack-http3-dos
first_seen: 2026-10-22
tags: [HTTP3프로토콜, 압축알고리즘, 서비스거부]
cves: []
---

**QPACK** HTTP/3 헤더 압축 알고리즘의 메모리 증폭 취약점으로 작은 HTTP 헤더가 메모리에서 최대 **4000배 크기**로 확장된다. 미인증 원격 공격자가 단일 연결만으로 서버 메모리를 고갈시켜 **서비스 거부(DoS)**를 유발할 수 있다.

## 타임라인

- 2026-10-22 [The Hacker News](https://thehackernews.com/2026/10/new-qpack-flaws-can-crash-http3-servers.html) — **FoxIO** QPACK 메모리 증폭 취약점 공개, 작동하는 PoC 코드 공개

## 관련
