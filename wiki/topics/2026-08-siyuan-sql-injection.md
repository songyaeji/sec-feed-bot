---
slug: siyuan-sql-injection
first_seen: 2026-08-03
tags: [SQL인젝션, 노트앱, 미인증접근, RCE, 크리티컬]
cves: [CVE-2026-69083, CVE-2026-69084, CVE-2026-69085, CVE-2026-72811]
---

# SiYuan 다중 SQL Injection 취약점

개인용 노트 앱 **SiYuan** v3.7.3 이전 버전에서 3개의 SQL injection 취약점이 발견되었다. 모두 CVSS 10.0의 심각한 취약점으로, 미인증 사용자 또는 publish RoleReader 토큰으로 접근 가능하며, 데이터베이스 쿼리를 직접 조작해 노트북 전체에 걸친 임의 데이터 읽기·수정·삭제가 가능하다.

## 타임라인

- 2026-08-03 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-69083) — CVE-2026-69083 fullTextSearchAssetContent endpoint SQL injection 공개 (CVSS 10.0)
- 2026-08-03 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-69084) — CVE-2026-69084 /api/search/searchEmbedBlock endpoint SQL injection 공개 (CVSS 10.0)
- 2026-08-03 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-69085) — CVE-2026-69085 /api/filetree/searchDocs endpoint SQL injection 공개 (CVSS 10.0)
- 2026-08-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-72811) — CVE-2026-72811 역링크 검색(backlink) SQL injection 추가 발견, v3.7.4 패치 (CVSS 10.0)

## 관련

[[siyuan-mcp-rce]] — SiYuan MCP 미인증 원격명령실행
