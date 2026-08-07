---
slug: wordpress-xss-php-rce
first_seen: 2026-08-07
tags: [WordPress, XSS, 사전인증, PHP코드실행]
cves: [CVE-2026-64638]
---

WordPress 로그인 화면의 **사전 인증 반사형 XSS 취약점**(CVE-2026-64638, CVSS 8.9)이 패치됐다. 모든 WordPress 버전에 영향을 주며, 특정 조건에서 PHP 코드 실행으로 체인될 수 있다. 공격자 권한 불필요, 높은 심각도의 원격 취약점. pwn.ai에 따르면 이미 악용 중인 것으로 보고됨.

## 타임라인

- 2026-08-07 [The Hacker News](https://thehackernews.com/2026/08/new-wordpress-pre-auth-xss-could-lead.html) — New WordPress Pre-Auth XSS Could Lead to PHP Code Execution - Patch ASAP

## 관련
