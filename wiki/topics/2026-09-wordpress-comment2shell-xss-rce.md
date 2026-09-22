---
slug: wordpress-comment2shell-xss-rce
first_seen: 2026-09-22
tags: [광범위배포소프트웨어, 코어취약점, XSS-RCE연쇄]
cves:
  - CVE-2026-93485
---

**WordPress 코어** 취약점(CVE-2026-93485 "Comment2Shell")으로 미인증 방문자가 댓글 필드에 악의적 스크립트 삽입 가능. 로그인한 관리자가 해당 페이지 방문 시 스크립트가 서버에서 실행되어 웹사이트 전체 장악 가능. WordPress 7.1.1에서 9월 17일 긴급 수정, 즉시 업데이트 권고.

## 타임라인

- 2026-09-22 [The Hacker News](https://thehackernews.com/2026/09/wordpress-comment2shell-flaw-can-turn.html) — WordPress Comment2Shell(CVE-2026-93485) XSS→RCE 연쇄 취약점 공개 및 패치

## 관련
