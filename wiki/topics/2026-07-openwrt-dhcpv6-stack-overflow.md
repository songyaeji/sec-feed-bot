---
slug: openwrt-dhcpv6-stack-overflow
first_seen: 2026-07-28
tags: [RCE, 라우터펌웨어, CVE, 스택오버플로우]
cves: [CVE-2026-53921]
---

OpenWrt 24.10.8에서 CVSS 9.8 중대도로 평가된 DHCPv6 스택 오버플로우 취약점 패치. odhcpd 프로세스의 기본 활성화 상태에서 인증 없이 스택 버퍼 덮어쓰기로 루트 권한 코드 실행 가능.

## 타임라인

- 2026-07-28 [The Hacker News](https://thehackernews.com/2026/07/critical-openwrt-dhcpv6-flaw-could-let.html) — CVE-2026-53921 스택 오버플로우 취약점 공개, 24.10.8 버전 긴급 패치

## 관련
