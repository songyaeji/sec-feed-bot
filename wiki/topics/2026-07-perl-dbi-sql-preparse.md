---
slug: perl-dbi-sql-preparse
first_seen: 2026-07-08
tags: [Perl, 데이터베이스, SQL preparse]
cves: [CVE-2026-14739, CVE-2026-14740]
---

Perl **DBI**(Data Base Interface) 1.650 이전 버전의 SQL 사전파싱(preparse) 과정에서 두 가지 메모리 안전 취약점 발생. 플레이스홀더 처리 시 **힙 오버플로우**(CVE-2026-14739)와 주석 삭제 중 **범위 초과 읽기**(CVE-2026-14740).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14739) — CVE-2026-14739: 극도로 많은 플레이스홀더 처리 시 힙 오버플로우 (CVSS 9.8)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14740) — CVE-2026-14740: SQL 주석 삭제 중 1바이트 범위 초과 읽기 (CVSS 9.1)

## 관련
