---
slug: surrealdb-default-permissions
first_seen: 2026-07-18
tags: [데이터베이스보안, 권한설정실수, SurrealDB]
cves: [CVE-2023-54366]
---

SurrealDB 1.0.1 이전 버전에서 신규 테이블의 기본 권한이 NONE 대신 FULL로 설정되어 있던 설정 실수. 인증된 사용자뿐 아니라 공개 인스턴스의 경우 미인증 접근자도 SELECT, CREATE, UPDATE, DELETE 권한을 갖게 됨.

## 타임라인

- 2026-07-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2023-54366) — CVE-2023-54366 공개 및 분석

## 관련

[[surrealdb-security]]
