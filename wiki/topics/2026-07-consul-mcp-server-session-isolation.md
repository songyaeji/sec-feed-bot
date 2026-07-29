---
slug: consul-mcp-server-session-isolation
first_seen: 2026-07-29
tags: [Consul, MCP, 세션격리, 인증우회]
cves: [CVE-2026-16326]
---

Consul MCP Server의 stateless 모드에서 세션 상태가 제대로 격리되지 않는 취약점이 발견됐다. 한 클라이언트의 Consul 인증 토큰이 다른 클라이언트의 후속 요청에 재사용될 수 있으며, 0.1.4 버전에서 수정됐다.

## 타임라인

- 2026-07-29 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16326) — CVE-2026-16326 공개, stateless 모드 세션 격리 실패 (CVSS 10.0)
