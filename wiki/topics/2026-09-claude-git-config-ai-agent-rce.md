---
slug: claude-git-config-ai-agent-rce
first_seen: 2026-09-02
tags: [AI에이전트보안, .git취약점, 코드실행]
cves: []
---

Manifold Security가 7개 AI 코딩 에이전트(**Claude, Codex, Cursor** 등)의 저장소 **.git 설정 파일** 악용 취약점을 공개했다. 저장소의 Git 설정에서 지정된 명령을 에이전트가 개발자 권한으로 실행해 샌드박스 외부에서 공격자 코드가 실행되며, 승인 프롬프트가 없다. 공개 당시 4개 에이전트가 여전히 미패치 상태.

## 타임라인

- 2026-09-02 [The Hacker News](https://thehackernews.com/2026/09/malicious-git-configs-can-make-claude.html) — Manifold Security, AI 코딩 에이전트 .git 설정 명령 주입 취약점 8개 공개, 4개 미패치

## 관련
