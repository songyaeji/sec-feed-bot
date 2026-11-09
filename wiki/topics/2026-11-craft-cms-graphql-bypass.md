---
slug: craft-cms-graphql-bypass
first_seen: 2026-11-08
tags: [권한우회, 정보유출, GraphQL, CVE-2026-124427]
cves: [CVE-2026-124427]
---

**Craft CMS** 5.0.0~5.11.2의 GraphQL 구현에서 익명 클라이언트가 prev/next 필드를 통해 범위 외(out-of-scope) 섹션 항목을 조회할 수 있는 권한 우회 취약점이 발견되었다. 공격자가 보이는 범위 내 항목에서 시작하여 연쇄적으로 next 필드를 따라가며 미공개 섹션의 제목·슬러그·커스텀 필드 콘텐츠를 추출 가능하다.

## 타임라인

- 2026-11-08 [NVD CVE-2026-124427](https://nvd.nist.gov/vuln/detail/CVE-2026-124427) — Craft CMS 5.0.0~5.11.2 GraphQL 권한 검증 우회 CVSS 9.8
