---
slug: bmc-ipmi-password-hash-exposure
first_seen: 2026-07-28
tags: [취약점, 서버관리, 원격관리인터페이스, 레거시취약점]
cves: []
---

약 36,900개의 인터넷 노출 서버 BMC 중 24,650개가 20년 된 IPMI 레거시 취약점으로 인해 인증 전에 암호 해시를 유출하고 있다. 감염된 BMC의 자격증명을 탈취하면 서버 펌웨어 수준의 접근권 획득 가능.

## 타임라인

- 2026-07-28 [BleepingComputer](https://www.bleepingcomputer.com/news/security/over-24-000-exposed-server-bmcs-leak-password-hash-via-decades-old-flaw/) — 24,000개 이상 노출된 BMC 패스워드 해시 유출 경보
- 2026-07-28 [The Hacker News](https://thehackernews.com/2026/07/24650-internet-exposed-bmcs-disclose.html) — Nozomi Networks Labs 조사, 36,872개 노출 BMC 중 24,650개 하시 노출 확인

## 관련
