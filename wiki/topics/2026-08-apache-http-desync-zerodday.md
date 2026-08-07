---
slug: apache-http-desync-zerodday
first_seen: 2026-08-07
tags: [제로데이, HTTP스머글링, Desync, RCE]
cves: []
---

**PortSwigger**의 AI 지원 보안 연구 시스템 'HTTP Terminator'가 HTTP 역직렬화(Desync) 공격의 새로운 기법을 발견했으며, 동시에 **Apache Traffic Server**에 대한 별도의 제로데이 취약점이 노출됐다. 30,000개 공격 벡터를 탐색한 결과 HTTP 프로토콜 구현 편차를 악용하는 스머글링 기법이 신규 공격 수법으로 확산될 가능성이 제기되고 있다.

## 타임라인

- 2026-08-07 [The Hacker News](https://thehackernews.com/2026/08/ai-assisted-http-terminator-finds-novel.html) — HTTP Terminator로 30,000개 벡터 탐색 후 HTTP Desync 신기법 및 Apache 제로데이 발견
