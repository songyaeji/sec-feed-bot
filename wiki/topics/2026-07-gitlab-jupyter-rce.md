---
slug: gitlab-jupyter-rce
first_seen: 2026-07-25
tags: [RCE, 제로데이, 개발도구]
cves: []
---

자관 GitLab 18.11.3에서 Jupyter 노트북 diff 기능의 취약점을 악용해 git 권한으로 임의 명령 실행 가능. 인증된 사용자만 필요하고 CI/CD 권한·관리자 권한 불필요.

## 타임라인

- 2026-07-25 [The Hacker News](https://thehackernews.com/2026/07/researcher-publishes-gitlab-rce-poc.html) — 보안 연구자 Yuhang Wu, GitLab Jupyter RCE PoC 공개

## 관련

- [[development-tool-exploits]]
- [[rce-vulnerabilities]]
