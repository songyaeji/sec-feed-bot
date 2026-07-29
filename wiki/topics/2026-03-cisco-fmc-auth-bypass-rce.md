---
slug: cisco-fmc-auth-bypass-rce
first_seen: 2026-03-04
tags: [Cisco, FMC, 인증우회, RCE]
cves: [CVE-2026-20079]
---

Cisco Secure Firewall Management Center(FMC) 웹 인터페이스의 부적절한 시스템 프로세스로 인한 미인증 원격 코드 실행 취약점이 발견됐다. 공격자가 부팅 시 생성되는 시스템 프로세스를 악용해 HTTP 요청으로 스크립트를 실행하고 운영체제에 대한 root 접근을 획득할 수 있다.

## 타임라인

- 2026-03-04 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-20079) — CVE-2026-20079 공개, 웹 인터페이스 인증 우회 및 RCE (CVSS 10.0)

## 관련

[[cisco-fmc-hardcoded-password]]
