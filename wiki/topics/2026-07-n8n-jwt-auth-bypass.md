---
slug: n8n-jwt-auth-bypass
first_seen: 2026-07-16
tags: [n8n, 인증우회, 토큰검증, Enterprise]
cves: []
---

**n8n** Enterprise 워크플로우 자동화 플랫폼의 JWT 검증 결함으로 다중 외부 발급자 신뢰 환경에서 **발급자 정보를 무시**하고 sub 클레임만 검증, 토큰 발급자 A의 유효한 JWT로 발급자 B의 사용자 계정에 로그인 가능.

## 타임라인

- 2026-07-16 [The Hacker News](https://thehackernews.com/2026/07/n8n-token-exchange-flaw-could-let.html) — n8n Enterprise JWT 발급자 검증 결함, 다중 발급자 환경서 계정 탈취

## 관련
