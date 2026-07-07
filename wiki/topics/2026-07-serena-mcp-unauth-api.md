---
slug: serena-mcp-unauth-api
first_seen: 2026-07-07
tags: [code editing tool, unauthenticated API, Flask]
cves: [CVE-2026-49471]
---

Serena MCP 코딩 도구의 웹 대시보드 미인증 API 노출 취약점. 내장 Flask API가 고정 포트에서 인증 없이 노출되며 CSRF 보호 및 호스트 헤더 검증 부재. DNS rebind 공격으로 로컬 코드 편집 및 실행 권한 획득 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-49471) — CVE-2026-49471 공개 (CVSS 8.3)
