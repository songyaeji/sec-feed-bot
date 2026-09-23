---
slug: cpanel-caldav-carddav-rce
first_seen: 2026-09-23
tags: [호스팅컨트롤판, 권한상향, RCE, 칼다브, 카드다브]
cves: []
---

**cPanel**의 CalDAV·CardDAV 서비스와 WP Toolkit 플러그인에서 권한 제어 결함이 발견됐다. 제한된 호스팅 계정 사용자가 서버 루트 권한으로 임의 코드를 실행할 수 있으며, 다른 계정의 데이터베이스까지 조작 가능. 영향받는 모든 호스팅 고객 사이트 침해 위험.

## 타임라인

- 2026-09-23 [The Hacker News](https://thehackernews.com/2026/09/new-cpanel-flaw-lets-hosting-account_0272795595.html) — cPanel CalDAV/CardDAV 서비스 루트 RCE, WP Toolkit 데이터베이스 접근제어 결함 발표, 패치 공개

## 관련
