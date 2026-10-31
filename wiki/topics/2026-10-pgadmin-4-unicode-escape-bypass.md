---
slug: pgadmin-4-unicode-escape-bypass
first_seen: 2026-10-30
tags: [정규표현식우회, 명령주입, PostgreSQL관리도구]
cves: [CVE-2026-116241, CVE-2026-17566]
---

pgAdmin 4의 Import/Export Data 도구에서 쿼리 검증을 우회해 psql `\copy ... TO PROGRAM` 명령을 실행 가능하다. CVE-2026-17566의 이전 우회 패치를 재우회한 취약점으로, 이중 따옴표 문자열에서 백슬래시 이스케이프를 검증하지 않는다.

## 타임라인

- 2026-10-30 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-116241) — CVE-2026-17566 패치 우회, 이중 따옴표 식별자에서 백슬래시 검증 미흡으로 psql PROGRAM 실행 가능, 버전 9.19 이상에서 패치

## 관련

없음
