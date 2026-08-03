---
slug: codeatro-sql-injection
first_seen: 2026-07-30
tags: [SQL인젝션, 회원관리시스템, 웹애플리케이션]
cves: [CVE-2025-69931]
---

# CodeAstro Membership Management System SQL Injection

**CodeAstro Membership Management System** 1.0에서 /delete_membership.php의 id 파라미터에 대한 입력값 검증이 부재해 SQL injection 취약점이 발생한다. CVSS 9.8의 심각한 취약점으로, 미인증 공격자가 데이터베이스 쿼리를 조작해 임의 데이터 접근·수정·삭제가 가능하다.

## 타임라인

- 2026-07-30 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-69931) — CVE-2025-69931 공개 (CVSS 9.8)

## 관련

없음
