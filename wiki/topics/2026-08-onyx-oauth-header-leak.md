---
slug: onyx-oauth-header-leak
first_seen: 2026-08-17
tags: [사용자토큰노출, AI플랫폼, 인증우회]
cves: [CVE-2026-71424]
---

# Onyx — OAuth 인증 헤더 노출 취약점

AI 플랫폼 **Onyx** 3.1.10, 3.2.14, 4.0.0 이전 버전의 MCP(Model Context Protocol) 서버 엔드포인트에서 다른 사용자의 OAuth 인증 헤더가 노출된다. OnyxTokenStorage가 사용자별 토큰을 공유 관리 MCPConnectionConfig 행에 복사한 뒤, _db_mcp_server_to_api_mcp_server가 이를 기본 접근(BASIC_ACCESS) 권한만 있는 모든 사용자에게 반환한다. 공격자는 다른 사용자의 OAuth 인증 헤더를 탈취해 권한 상승 및 계정 탈취 가능.

## 타임라인

- 2026-08-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71424) — CVE-2026-71424 CVSS 9.6 공개, 사용자 OAuth 헤더 노출 취약점 확인
