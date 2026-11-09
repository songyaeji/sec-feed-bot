---
slug: openemr-sql-injection
first_seen: 2026-11-08
tags: [SQL인젝션, 의료정보, 환자데이터유출, CVE-2026-124469]
cves: [CVE-2026-124469]
---

**OpenEMR** 8.3.0 이전 버전의 청구서 모듈 의약품 조회(DrugSalesService::sellDrug)에서 POST 파라미터 prod[N][warehouse]가 SQL ORDER BY 절에 직접 보간되는 SQL 인젝션 취약점이 발견되었다. 저권한 인증 사용자가 시간 기반 블라인드 오라클로 환자 기록과 사용자 암호 bcrypt 해시를 추출 가능하다.

## 타임라인

- 2026-11-08 [NVD CVE-2026-124469](https://nvd.nist.gov/vuln/detail/CVE-2026-124469) — OpenEMR 8.3.0 이전 청구서 모듈 SQL 인젝션 CVSS 9.9
