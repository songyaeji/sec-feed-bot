---
slug: itsourcecode-enrollment-system-sqli
first_seen: 2026-04-10
tags: [SQLinjection, 웹애플리케이션, 학사관리시스템, 다중취약점]
cves: [CVE-2026-36232, CVE-2026-36233, CVE-2026-36234]
---

# itsourcecode Online Student Enrollment System SQL 인젝션

**itsourcecode Online Student Enrollment System v1.0**에서 발견된 SQL 인젝션 취약점 3건(CVSS 9.8).

**CVE-2026-36232**: instructorClasses.php의 'classId' GET 파라미터가 sanitization 없이 SQL 쿼리에 직결됨.

**CVE-2026-36233**: assignInstructorSubjects.php의 'subjcode' 파라미터가 적절한 검증 없이 SQL에 직결됨.

**CVE-2026-36234**: newCourse.php의 'coursename' 파라미터 SQL 인젝션.

모두 학사 관리 기능을 대상으로 하며 데이터베이스 접근 및 정보 유출 위험.

## 타임라인

- 2026-04-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-36232) — CVE-2026-36232 공개 (CVSS 9.8)
- 2026-04-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-36233) — CVE-2026-36233 공개 (CVSS 9.8)
- 2026-04-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-36234) — CVE-2026-36234 공개 (CVSS 9.8)
