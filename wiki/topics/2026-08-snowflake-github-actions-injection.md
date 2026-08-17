---
slug: snowflake-github-actions-injection
first_seen: 2026-08-17
tags: [CI_CD파이프라인취약점, 자격증명탈취, 명령주입]
cves: []
---

Wiz 보안연구팀이 Snowflake 공개 리포지터리의 GitHub Actions 워크플로우에서 **command injection** 취약점 발견. 조작된 GitHub issue를 통해 내부 **Jira 자격증명** 노출 위험.

## 타임라인

- 2026-08-17 [The Hacker News](https://thehackernews.com/2026/08/snowflake-github-actions-flaw-lets_0330881554.html) — Snowflake 리포지터리 `.github/workflows/jira_issue.yml` 워크플로우 command injection 취약점, 조작된 issue로 내부 Jira 자격증명 접근 가능

## 관련
