---
slug: mcp-python-sdk-oauth-credential-theft
first_seen: 2026-09-29
tags: [공급망공격, 개발자도구, 자격증명탈취, API보안]
cves: []
---

Anthropic의 공식 **MCP(Model Context Protocol) Python SDK**에 취약점이 발견됐다. 악의적인 MCP 서버가 SDK 기반 애플리케이션의 OAuth 자격증명(클라이언트 시크릿, 인증 코드, PKCE 증명 키)을 완벽히 탈취할 수 있다. AI 개발 도구의 공급망 위험을 드러낸다.

## 타임라인

- 2026-09-29 [The Hacker News](https://thehackernews.com/2026/09/official-mcp-python-sdk-flaw-can-let.html) — MCP Python SDK OAuth 자격증명 탈취 취약점 공개, 버전 1.30.0 이상에서 수정

## 관련

[[mcp-server-ai-exfiltration]]
