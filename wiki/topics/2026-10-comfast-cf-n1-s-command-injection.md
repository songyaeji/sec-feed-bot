---
slug: comfast-cf-n1-s-command-injection
first_seen: 2026-10-16
tags: [IoT, router, command injection, RCE]
cves: [CVE-2026-77683]
---

Comfast CF-N1-S 무선 공유기의 NTP 타임존 설정 기능에서 발견된 명령 인젝션 취약점. 시스템 함수의 timestr 인자 조작으로 임의 명령 실행 가능하며 원격 공격 가능.

## 타임라인

- 2026-08-21 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-77683) — CVE-2026-77683: Comfast CF-N1-S 2.6.0.1 /cgi-bin/mbox-config 시스템 함수 timestr 인자 명령 인젝션 (CVSS 9.9, 공개 익스플로잇 있음)

## 관련
