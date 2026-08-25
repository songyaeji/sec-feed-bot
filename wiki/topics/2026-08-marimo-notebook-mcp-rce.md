---
slug: marimo-notebook-mcp-rce
first_seen: 2026-08-25
tags: [노트북앱, 명령주입, MCP악용, 고심각도]
cves: []
---

# Marimo Notebook — 편집 모드 MCP 명령 실행 취약점

**Marimo** 노트북 소프트웨어에서 고심각도 보안 결함이 발견됐다. 공격자가 악의적으로 조작한 노트북을 편집 모드(edit mode)로 열 때, **Model Context Protocol(MCP)** 명령이 검증 없이 로컬 서브프로세스로 즉시 실행된다.

## 타임라인

- 2026-08-25 [The Hacker News](https://thehackernews.com/2026/08/marimo-notebook-flaw-could-run-mcp.html) — Marimo 고심각도 MCP 명령 실행 취약점 공개, VulnCheck CNA 기록

## 관련
