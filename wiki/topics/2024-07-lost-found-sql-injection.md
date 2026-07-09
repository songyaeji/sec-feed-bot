---
slug: lost-found-sql-injection
first_seen: 2024-07-29
tags: [권한상향, SQL주입]
cves: [CVE-2024-37857]
---

# Lost and Found Information System SQL 인젝션 권한상향

Lost and Found Information System v1.0에서 발견된 SQL 인젝션 취약점. **view_category.php**의 **id** 파라미터 검증 부재로 원격 공격자가 권한상향 가능(CVSS 8.8).

## 타임라인

- 2024-07-29 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-37857) — CVE-2024-37857: Lost and Found v1.0 view_category.php SQL 인젝션
