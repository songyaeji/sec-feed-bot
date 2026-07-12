---
slug: dify-sql-injection
first_seen: 2026-07-10
tags: [SQL인젝션, AI플랫폼, 데이터손상, LLM]
cves: [CVE-2026-61461]
---

**Dify** LLM 애플리케이션 플랫폼(< 1.16.0-rc1) MyScale 벡터 스토어 백엔드의 SQL 인젝션. `search_by_full_text` 메서드가 검색 파라미터를 이스케이프·파라미터화 없이 직접 사용. 공격자가 악의적 SQL을 검색 파라미터에 주입해 ClickHouse 데이터베이스 읽기·수정·삭제 가능 (CVSS 8.8). 수정본: 1.16.0-rc1.

## 타임라인

- 2026-07-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-61461) — CVE-2026-61461 공개

## 관련
