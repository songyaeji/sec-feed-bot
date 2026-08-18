---
slug: comfast-cf-n1-s-command-injection
first_seen: 2026-08-18
tags: [명령주입, 라우터, RCE, 원격접근가능]
cves: [CVE-2026-75094]
---

# COMFAST CF-N1-S — CGI 인터페이스 OS 명령 주입

무선 라우터 **COMFAST CF-N1-S** 2.6.0.1 버전의 /cgi-bin/mbox-config?method=SET&section=ptest_ssid CGI 인터페이스에서 OS 명령 주입 취약점이 발견됐다. 사용자 입력값인 ssid 인수가 검증 없이 명령 구성에 포함되면서 원격 공격자가 임의 명령을 실행할 수 있다. 취약점에 대한 익스플로잇이 이미 공개되어 실제 악용 위험이 높다.

## 타임라인

- 2026-08-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-75094) — CVE-2026-75094 CVSS 9.1 공개, CGI 명령 주입 취약점 및 공개 익스플로잇 확인
