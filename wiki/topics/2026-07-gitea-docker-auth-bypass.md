---
slug: gitea-docker-auth-bypass
first_seen: 2026-07-06
tags: [gitea, vulnerability, docker, authentication]
cves: [CVE-2026-20896]
---

Gitea Docker 이미지의 임계 취약점 **CVE-2026-20896** (CVSS 9.8). 신뢰되지 않은 `X-WEBAUTH-USER` 헤더를 신뢰하는 설정 오류로 인증 우회 가능. 공개 13일 후 악성 행위자 탐사 시작.

## 타임라인

- 2026-07-06 [The Hacker News](https://thehackernews.com/2026/07/threat-actors-probe-gitea-docker-flaw.html) — Sysdig가 악용 시도 탐지

## 관련

