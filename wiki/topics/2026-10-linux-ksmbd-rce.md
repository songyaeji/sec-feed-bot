---
slug: linux-ksmbd-rce
first_seen: 2026-10-22
tags: [리눅스커널, 미패치, SMB서버]
cves: [ZDI-CAN-33774, ZDI-CAN-33549]
---

Linux 커널의 **KSMBD** SMB 서버에서 2개의 **미패치 원격코드실행(RCE)** 취약점이 공개됐다. 하나는 사전 인증 없이 트리거 가능하며, 두 취약점 모두 CVSS 9.0으로 심각도가 높다. 현재 mainline 커널에는 수정이 적용되지 않았다.

## 타임라인

- 2026-10-22 [The Hacker News](https://thehackernews.com/2026/10/two-cvss-90-linux-ksmbd-rce-flaws.html) — **KSMBD** 2개 미패치 CVSS 9.0 RCE 취약점(ZDI-CAN-33774, ZDI-CAN-33549) 공개, mainline 커널 미패치

## 관련
