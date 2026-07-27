---
slug: pheditor-rce
first_seen: 2026-07-27
tags: [Pheditor, PHP, 원격코드실행, 명령인젝션]
cves: [CVE-2026-48030]
---

PHP 단일 파일 편집기 Pheditor 버전 2.0.1~2.0.3의 터미널 액션 핸들러에서 'dir' POST 매개변수에 대한 쉘 메타문자 인젝션 방어 부재. 인증된 사용자가 TERMINAL_COMMANDS 화이트리스트를 완전히 우회하고 웹 서버 권한으로 임의 OS 명령을 실행할 수 있다. 버전 2.0.4에서 패치됨.

## 타임라인

- 2026-07-27 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-48030) — CVE-2026-48030 공개 (CVSS 9.9)
