---
slug: bieticaret-sql-injection
first_seen: 2026-07-09
tags: [이커머스, SQLInjection, 높은심각도, 데이터유출]
cves: [CVE-2026-5955]
---

Inrove Software의 이커머스 플랫폼 **BiEticaret** 3.3.57 이전 버전에서 **SQL 인젝션** 취약점 발견. CVSS 9.8(Critical)로 최고 심각도. 공격자가 입력값을 조작해 데이터베이스를 직접 조회하고 변조할 수 있으며, 결제 정보, 고객 개인정보 유출로 직결될 수 있다.

## 타임라인

- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-5955) — CVE-2026-5955: SQL 인젝션 (CVSS 9.8, 3.3.57 이전)
