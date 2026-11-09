---
slug: wordpress-patch-installation-rce-window
first_seen: 2026-11-06
tags: [WordPress, RCE, 패치우회]
cves: []
---

**WordPress** 보안 업데이트 설치 과정에서 **구 코드**로 파일을 압축 해제하는 문제. 공격자가 정확한 타이밍에 웹 요청을 보내면 설치 중에 명령 실행이 가능하며, 보안 연구자는 설치 중 웹 접근 차단을 권장한다.

## 타임라인

- 2026-11-06 [The Hacker News](https://thehackernews.com/2026/11/installing-fix-for-exploited-wordpress.html) — WordPress 패치 설치 중 **RCE** 윈도우, Picus Security 연구원 공개

## 관련
