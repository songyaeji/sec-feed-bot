---
slug: nextcloud-collabora-code-rce
first_seen: 2026-10-14
tags: [RCE, Nextcloud, 오픈소스]
cves: []
---

**Nextcloud** 옵션 앱 **Collabora Online - Built-in CODE Server**의 취약점을 악용해 Nextcloud 서버에 웹셸을 심는 공격이 진행 중이다. 공격자는 웹 셸을 통해 웹 서버 권한으로 임의 명령 실행이 가능하며, 첫 공격이 2026년 9월 10일 기록되었다. 3명의 관리자가 GitHub에서 보고했으며, 서버 침해의 시작점으로 이용되는 사건.

## 타임라인

- 2026-09-10 [GitHub Issues](https://github.com/nextcloud/server/issues) — Nextcloud 관리자 3명, Collabora Online CODE Server 웹셸 침해 첫 보고
- 2026-10-14 [The Hacker News](https://thehackernews.com/2026/10/hackers-backdoor-nextcloud-servers.html) — 웹셸 배포 공격 공개 분석, 광범위 감염 우려
