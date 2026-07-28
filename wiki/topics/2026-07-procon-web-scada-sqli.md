---
slug: procon-web-scada-sqli
first_seen: 2026-07-28
tags: [SCADA, 산업제어, SQL인젝션, 미인증]
cves: [CVE-2026-16462]
---

**PROCON-WEB SCADA** 시스템의 `GetGridData` 엔드포인트가 적절히 삭제(sanitize)되지 않아 **미인증 공격자가 임의 SQL 명령 실행** 가능. CVSS 9.8.

## 타임라인

- 2026-07-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16462) — CVE-2026-16462 공개 (CVSS 9.8, PROCON-WEB 미인증 SQL 인젝션)

## 관련

- [[scada-sql-injection]]
