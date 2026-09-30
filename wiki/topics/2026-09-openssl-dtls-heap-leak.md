---
slug: openssl-dtls-heap-leak
first_seen: 2026-09-30
tags: [취약점, OpenSSL, UDP암호화]
cves: []
---

# OpenSSL — DTLS 힙 메모리 누출 취약점

**OpenSSL**이 2026년 9월 29일 공개한 고심각도 취약점으로, **DTLS**(UDP 기반 TLS) 프로토콜에서 핸드셰이크 메시지 재송신 중 메모리 누출 또는 프로그램 충돌이 발생할 수 있다. IoT·VPN 등 광범위한 장비에서 사용되는 프로토콜이다.

## 타임라인

- 2026-09-30 [The Hacker News](https://thehackernews.com/2026/09/openssl-fixes-high-severity-dtls-flaw.html) — OpenSSL DTLS 힙 메모리 누출 고심각도 취약점 패치 발표

## 관련
