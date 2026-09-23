---
slug: ubuntu-kernel-unix-socket-escape
first_seen: 2026-09-23
tags: [리눅스커널, 컨테이너탈출, CVE, 우분투, 미패치]
cves: [CVE-2026-80521]
---

**Linux 커널** AF_UNIX 소켓 서브시스템의 use-after-free 결함으로 컨테이너 탈출 및 호스트 루트 권한 획득이 가능하다. 취약점 CVE-2026-80521 (CVSS 7.8)은 8월 6일 업스트림 커널에서 수정됐으나, Ubuntu 26.04, 24.04, 22.04 LTS 버전이 여전히 미패치 상태. 공개 익스플로잇 릴리스로 대규모 위협.

## 타임라인

- 2026-09-23 [The Hacker News](https://thehackernews.com/2026/09/exploit-released-for-unpatched-ubuntu.html) — DepthFirst 보안연구 CVE-2026-80521 공개 익스플로잇 발표, Ubuntu LTS 미패치 상태 강조

## 관련
