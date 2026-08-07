---
slug: linux-sctp-use-after-free
first_seen: 2026-08-07
tags: [Linux kernel, SCTP, 사용후해제, 컨테이너탈출]
cves: []
---

Linux 커널 SCTP 네트워킹 코드의 **18년 된 사용 후 해제(use-after-free) 취약점**이 패치됐다. 텐센트 연구팀이 이 취약점을 이용해 호스트에서 루트 권한 획득 및 컨테이너 탈출을 입증했다. 2008년부터 존재했던 결함으로, 2026년 8월 3일 안정 커널(7.1.6, 6.18.42, 6.12.101, 6.6.148)에서 수정됨. SCTP에 접근 가능한 구성의 경우 즉시 업데이트 필요.

## 타임라인

- 2026-08-07 [The Hacker News](https://thehackernews.com/2026/08/18-year-old-linux-sctp-flaw-could-let.html) — 18-Year-Old Linux SCTP Flaw Could Let Local Users Gain Root and Escape Containers

## 관련
