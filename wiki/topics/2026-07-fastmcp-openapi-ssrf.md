---
slug: fastmcp-openapi-ssrf
first_seen: 2026-07-08
tags: [MCP, AI에이전트, SSRF]
cves: [CVE-2026-32871]
---

MCP(Model Context Protocol) 서버 구축 도구 **FastMCP** 3.2.0 이전 버전의 OpenAPIProvider에서 입력 검증이 부족하다. RequestDirector가 외부 입력으로 백엔드 서비스에 HTTP 요청을 구성할 때 **SSRF**(서버 요청 위조) 공격이 가능하다(CVSS 10.0).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-32871) — CVE-2026-32871 공개

## 관련
