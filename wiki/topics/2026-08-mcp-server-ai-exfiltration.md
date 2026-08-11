---
slug: mcp-server-ai-exfiltration
first_seen: 2026-08-11
tags: [AI, MCP, AI에이전트, 정보탈취, C2채널, 명령분산]
cves: []
---

악의적인 **MCP(Model Context Protocol) 서버**가 AI 코딩 어시스턴트에 연결되면, 명령을 **여러 조각으로 분산**해 직관적인 악의 신호를 숨기고 **SSH 키, 환경 변수, 소스 코드, 고객 데이터**를 탈취할 수 있다. 단일 요청이 거부되어도 분석된 요청들을 AI가 정상 작업으로 해석해 정보 유출을 우회할 수 있다.

## 타임라인

- 2026-08-11 [The Hacker News](https://thehackernews.com/2026/08/malicious-mcp-servers-can-split.html) — MCP 서버의 명령 분산 기법으로 AI 에이전트 정보탈취 공격 분석

## 관련
