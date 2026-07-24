---
slug: redis-kimi-k3-zerodday
first_seen: 2026-07-24
tags: [제로데이, RCE, AI기술]
cves: []
---

AI 에이전트 Kimi K3가 Redis 메모리 관리 결함 기반의 원격 코드 실행 제로데이 여러 개를 발견했다. 연구자들이 인증된 RCE PoC를 공개했으며, Redis 6.2.22, 7.4.9, 8.6.4, 8.8.0 등 여러 버전이 영향받는다. 공격자가 RESTORE 명령과 특정 조합(EVAL, XGROUP, RedisBloom 모듈 등)으로 악용 가능하다. Redis가 긴급 패치를 공개했다.

## 타임라인

- 2026-07-24 [The Hacker News](https://thehackernews.com/2026/07/kimi-k3-agents-found-redis-zero-days.html) — Kimi K3 에이전트가 Redis 메모리 결함 제로데이 발견 및 RCE PoC 공개. Redis 6.2.23, 7.2.15, 7.4.10 등 패치 릴리스

## 관련
