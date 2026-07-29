---
slug: gitea-git-hook-rce
first_seen: 2026-07-29
tags: [Gitea, RCE, 권한상향]
cves:
  - CVE-2026-60004
---

자체호스팅 Git 플랫폼 **Gitea**의 원격코드실행 취약점이 1.27.1에서 패치되었다. 저장소 쓰기 권한을 가진 이용자가 공격자 제어 패치 내용을 Git 훅으로 변환해 Gitea 서비스 계정 권한으로 셸 명령을 실행할 수 있다. 1.17 이상 1.27.1 이전 버전이 영향받는다.

## 타임라인

- 2026-07-29 [The Hacker News](https://thehackernews.com/2026/07/new-gitea-rce-lets-repository-writers.html) — Gitea Git 훅 RCE 취약점 패치, CVE-2026-60004 (CVSS 9.8)

## 관련

[[gitlab-jupyter-rce]] — Git 플랫폼 RCE 취약점
