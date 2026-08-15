---
slug: geoserver-sqli-rce-zerodday
first_seen: 2026-08-15
tags: [제로데이, SQL injection, RCE]
cves: []
---

오픈소스 지리정보 서버 **GeoServer**의 `jsonArrayContains` 함수에서 미인증 SQL injection 제로데이 발견. 공격자가 조작된 요청을 통해 SQL 인젝션을 수행할 수 있으며, 서버·데이터베이스 구성에 따라 원격코드실행(RCE)으로 이어질 가능성. 공개 수시간 내 인터넷 노출 시스템에 대한 공격 탐사 수백 건 포착, 아직 공식 패치 없음.

## 타임라인

- 2026-08-15 [Security Affairs](https://securityaffairs.com/?p=197216) — 미인증 SQL injection·RCE 제로데이 공개, 공격자 탐사 진행 중
- 2026-08-15 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208067) — 제로데이 공개 후 수백 건 공격 탐색 포착

## 관련

(없음)
