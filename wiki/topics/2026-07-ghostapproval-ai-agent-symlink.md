---
slug: ghostapproval-ai-agent-symlink
first_seen: 2026-07-09
tags: [AI, 코딩에이전트, symlink, 권한상향, RCE]
cves: []
---

보안 연구 기관 Wiz 발견, **Amazon Q**, **GitHub Copilot**, **Claude Code** 등 6개 인기 AI 코딩 어시스턴트에서 symlink 속임수 공격 가능. 개발자의 파일 쓰기 권한 요청을 일반 파일로 위장했다 실제는 시스템 민감 파일에 쓰기 수행하여 컴퓨터 탈취 가능.

## 타임라인

- 2026-07-09 [The Hacker News](https://thehackernews.com/2026/07/ghostapproval-symlink-flaws-could-let.html) — 6개 AI 코딩 에이전트의 symlink 권한 상향 취약점 발견

## 관련

[[friendly-fire-ai-agent-rce]]
