---
slug: dhtmlx-pdf-export-rce
first_seen: 2026-05-15
tags: [DHTMLX, RCE, PDFExport, Node.js]
cves: [CVE-2026-41553]
---

DHTMLX Gantt 및 Scheduler에 사용되는 PDF Export Module의 data 파라미터 검증 미흡. 악의적 JavaScript 코드 주입으로 Node.js 서버에서 실행되어 서버 침해 가능.

## 타임라인

- 2026-05-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-41553) — CVE-2026-41553 공개 (CVSS 10.0, PDF Export Module 0.7.6에서 패치)
