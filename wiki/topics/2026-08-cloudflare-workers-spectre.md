---
slug: cloudflare-workers-spectre
first_seen: 2026-08-19
tags: [클라우드, 제로데이, 토큰탈취, Spectre]
cves: []
---

보안 연구자들이 **Cloudflare Workers** 환경에서 동일 호스트의 인접 Worker로부터 JWT 토큰을 추출하는 원격 Spectre 공격을 공개했다. 초당 12비트 속도로 민감정보를 유출하며, 2021년 이전 공격보다 360배 빠르다. 클라우드 격리 계층에서의 사이드채널 공격 위험을 시사한다.

## 타임라인

- 2026-08-19 [The Hacker News](https://thehackernews.com/2026/08/cloudflare-workers-spectre-attack-leaks.html) — Cloudflare Workers Spectre 공격으로 JWT 토큰 유출 시연, 2021년 대비 360배 빠른 속도

## 관련
