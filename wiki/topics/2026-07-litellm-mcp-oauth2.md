---
slug: litellm-mcp-oauth2
first_seen: 2026-07-08
tags: [AI, LLM, OAuth2인증우회]
cves: [CVE-2026-59822]
---

**LiteLLM** 1.84.0 이전 버전의 MCP Streamable HTTP 엔드포인트가 위조된 Authorization 헤더를 사용하면 OAuth2 패스스루 대체 경로로 빠져, 실패한 LiteLLM 키 검증을 우회하는 외부 인증 제공자 토큰으로 접근 가능한 취약점. 미인증 공격자가 이용할 수 있다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59822) — CVE-2026-59822 공개 (CVSS N/A)
