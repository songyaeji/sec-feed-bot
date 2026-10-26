---
slug: ruflo-mcp-rce
first_seen: 2026-07-09
tags: [개발도구, MCP보안, API보안, RCE]
cves: [CVE-2026-59726]
---

Anthropic Claude Code의 에이전트 meta-harness인 **Ruflo** 3.16.3 이전 버전이 기본 Docker 배포에서 MCP 브릿지 POST /mcp·POST /mcp/:group 엔드포인트를 미인증으로 노출해 terminal_execute 도구 호출·컨테이너 쉘 획득·MCP 제공자 API 키 탈취·AgentDB 학습 패턴 오염이 가능하다.

## 타임라인

- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59726) — CVE-2026-59726 공개, MCP 브릿지 미인증 도구 호출 RCE
