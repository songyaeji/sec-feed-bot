---
slug: terraform-mcp-server-cred-reuse
first_seen: 2026-07-28
tags: [terraform-mcp-server, MCP, 멀티테넌트, 크로스테넌트]
cves: [CVE-2026-16498]
---

**terraform-mcp-server** 1.1.0 이전 버전에서 streamable-HTTP stateless transport 모드의 **크로스 테넌트 자격증명 재사용 취약점**으로 한 사용자의 Terraform 토큰이 후속 사용자를 대신하여 도구 호출 실행에 악용될 수 있음. CVSS 10.0, 1.1.0 이상에서 수정.

## 타임라인

- 2026-07-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16498) — CVE-2026-16498 공개 (CVSS 10.0, terraform-mcp-server 1.1.0에서 수정)

## 관련

- [[mcp-protocol-security]]
