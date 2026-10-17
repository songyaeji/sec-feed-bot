---
slug: nginx-rce-memory-bugs
first_seen: 2026-10-15
tags: [RCE, 메모리버그, 웹서버, 패치필요]
cves: []
---

**NGINX**가 10월 14일 1.30.6, 1.31.7을 릴리스해 5개 취약점을 수정했다. 2005년 5월부터 모든 버전에 존재한 메모리 버그를 포함해, 메모리 누출, TLS 세션 위조로 클라이언트 인증서 검증 우회 등이 포함됐다.

## 타임라인

- 2026-10-14 [F5/NGINX](https://nginx.org/en/) — NGINX 1.30.6, 1.31.7 5개 취약점 보안 패치 발표
- 2026-10-15 [The Hacker News](https://thehackernews.com/2026/10/nginx-fixes-5-flaws-including-possible.html) — RCE, TLS 우회 포함 취약점 분석

## 관련
