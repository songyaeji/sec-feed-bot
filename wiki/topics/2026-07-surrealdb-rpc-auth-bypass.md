---
slug: surrealdb-rpc-auth-bypass
first_seen: 2026-07-18
tags: [데이터베이스보안, 인증우회, RCE]
cves: [CVE-2024-58362]
---

SurrealDB 1.5.5 (2.0.0-beta.3) 이전 버전의 RPC API signin/signup 메서드에서 임의 객체를 재귀적으로 검증하지 않아 발생하는 인증 우회 취약점. 공격자는 bincode 형식의 이진 객체로 서브쿼리를 인코딩해 미인증 상태에서 임의 쿼리 실행 가능. 비-IAM 리소스 전체에 CRUD 접근 가능.

## 타임라인

- 2026-07-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-58362) — CVE-2024-58362 공개 및 분석

## 관련

[[surrealdb-security]]
