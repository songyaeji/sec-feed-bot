---
slug: ai-copilot-oauth-bypass
first_seen: 2026-07-17
tags: [vulnerability, wordpress-plugin, oauth-auth-bypass]
cves: [CVE-2026-9810]
---

WordPress AI 어시스턴트 플러그인 AI Copilot 1.5.4 이하에서 OAuth 액세스 토큰과 WordPress 사용자 바인딩 부재로 인한 인증 우회. 미인증 공격자가 공개 OAuth 흐름을 완료한 후 그 토큰을 관리자 세션으로 사용해 임의 MCP 도구를 실행할 수 있다.

## 타임라인

- 2026-07-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-9810) — CVE-2026-9810 CVSS 9.8: AI Copilot에서 OAuth 토큰이 WordPress 사용자와 바인딩되지 않음, 미인증 공격자가 공개 OAuth 흐름으로 유효한 토큰 획득 후 관리자 권한 MCP 도구 실행 가능

## 관련
