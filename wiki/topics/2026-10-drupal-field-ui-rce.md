---
slug: drupal-field-ui-rce
first_seen: 2026-10-15
tags: [CMS취약점, RCE, 원격코드실행]
cves: []
---

Drupal Core의 Field UI 모듈에 PHP 역직렬화 취약점이 발견되었으며, 공개 폼을 통해 악의적 객체 주입이 가능하다. 로그인 없이도 악용할 수 있는 exploit path가 존재해 대규모 Drupal 설치 기반에 광범위한 위험이 발생했다.

## 타임라인

- 2026-10-14 [The Hacker News](https://thehackernews.com/2026/10/drupal-patches-critical-core-rce-flaw.html) — Drupal 긴급 패치 (11.4.10, 11.3.19, 10.6.19) 배포, Field UI 모듈 미인증 RCE, contributed modules 통한 exploit path 존재

## 관련

없음
