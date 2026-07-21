---
slug: rockwell-factorytalk-jwt
first_seen: 2026-07-21
tags: [산업제어, JWT, 인증우회, Rockwell]
cves: [CVE-2026-10714]
---

**Rockwell Automation FactoryTalk Services Platform (FTSP)** 6.60의 Okta JWT 서명 검증 결함. 공격자가 JWT 알고리즘을 "none"으로 설정해 위조 토큰으로 임의 사용자 가장 가능. 저권한 인증 사용자도 시스템 설정 접근 및 권한 부여 가능하며, 현재 보안 패치 미출시 상태.

## 타임라인

- 2026-07-21 [CISA ICSA-26-202-07](https://www.cisa.gov/news-events/ics-advisories/icsa-26-202-07) — Rockwell FactoryTalk Services Platform JWT 검증 우회 취약점 공개 및 보안 대책 권고

## 관련

[[rockwell-arena-rce]]
