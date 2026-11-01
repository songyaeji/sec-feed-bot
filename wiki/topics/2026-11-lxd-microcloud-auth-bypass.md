---
slug: lxd-microcloud-auth-bypass
first_seen: 2026-11-01
tags: [컨테이너화, 원격코드실행, 인증우회, CVSS10]
cves: []
---

Canonical의 **LXD**와 **MicroCloud** 컨테이너 관리 플랫폼에서 발견된 CVSS 10.0 치명적 취약점은 신뢰할 수 있는 클라이언트의 비공개 키 없이도 해당 클라이언트로 로그인할 수 있다. 공격자는 HTTPS API 네트워크 접근과 신뢰 클라이언트의 공개 인증서만 있으면 클러스터 및 가상머신을 완전히 제어할 수 있다.

## 타임라인

- 2026-11-01 [The Hacker News](https://thehackernews.com/2026/11/critical-lxd-and-microcloud-flaw-cvss.html) — **LXD·MicroCloud** **CVSS 10.0** 인증 우회, 신뢰 클라이언트 비공개 키 없이 로그인 가능, 클러스터·VM 제어 획득 가능

## 관련
