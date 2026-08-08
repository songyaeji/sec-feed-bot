---
slug: google-mcp-toolbox-auth-bypass
first_seen: 2026-07-31
tags: [인증우회, 고위험취약점, API보안]
cves: [CVE-2026-14537]
---

Google **MCP Toolbox** v1.3.0~v1.4.0에 부정확한 인증 검증 취약점이 발견됐다. 
--enable-api 플래그가 활성화된 경우 미인증 공격자가 레거시 HTTP 엔드포인트를 통해 
scopeRequired로 보호되는 도구를 직접 호출할 수 있다. CVSS 9.8 중대 취약점.

## 타임라인

- 2026-07-31 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14537) — CVE-2026-14537 공개

## 관련

[[ai-tool-sandbox-escapes]]
