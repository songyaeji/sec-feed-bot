---
slug: crmeb-sql-injection
first_seen: 2024-03-28
tags: [RCE, SQL주입, 이커머스]
cves: [CVE-2024-28714]
---

# CRMEB Java 이커머스 시스템 SQL 인젝션 원격코드실행

오픈소스 이커머스 플랫폼 CRMEB v1.3.4에서 발견된 SQL 인젝션 취약점. **groupid** 파라미터 검증 부재로 인증된 사용자가 임의 데이터 조작 및 코드 실행 가능(CVSS 8.1).

## 타임라인

- 2024-03-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-28714) — CVE-2024-28714: CRMEB v1.3.4 groupid 파라미터 SQL 인젝션
