---
slug: gitlab-issue-email-credential
first_seen: 2026-09-23
tags: [인증우회, GitLab, 코드저장소, 제로데이]
cves: []
---

GitLab이 사용자에게 이슈 제출용으로 제공하는 개인 이메일 주소가 사실상 자격증명으로 작동하는 취약점이 발견됐다. 이 주소로 이메일을 보내면 GitLab이 자신의 이름으로 커밋을 수행하고 CI/CD 작업을 트리거할 수 있어, 코드 리포지토리 장악으로 이어질 수 있다.

## 타임라인

- 2026-09-23 [The Hacker News](https://thehackernews.com/2026/09/a-leaked-gitlab-issue-email-address.html) — GitLab issue email 주소 노출 시 권한상향, 임의 브랜치 접근 및 CI/CD 실행 가능

## 관련

