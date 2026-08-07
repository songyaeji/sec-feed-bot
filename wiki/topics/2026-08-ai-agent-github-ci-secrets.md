---
slug: ai-agent-github-ci-secrets
first_seen: 2026-08-07
tags: [AI에이전트, CI파이프라인, 권한상향, 보안테스트]
cves: []
---

Novee Security가 **Claude Code, Gemini CLI, OpenAI 에이전트** 등 주요 AI 코딩 도구의 **CI/CD 파이프라인 접근 취약점**을 공개했다. 저권한 GitHub 계정의 이슈 개설만으로도 CI runner에서 임의 코드 실행, OpenAI의 경우 다음 agent run 하이재킹이 가능했다. 각 벤더의 기본 배포 설정에서 취약점 재현. Black Hat USA 2026 발표.

## 타임라인

- 2026-08-07 [The Hacker News](https://thehackernews.com/2026/08/claude-code-and-gemini-cli-flaws-let.html) — Claude Code and Gemini CLI Flaws Let a GitHub Issue Reach CI Workflow Secrets

## 관련
