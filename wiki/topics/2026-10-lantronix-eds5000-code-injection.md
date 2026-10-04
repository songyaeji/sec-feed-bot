---
slug: lantronix-eds5000-code-injection
first_seen: 2026-06-23
tags: [ICS, Network Device, RCE]
cves: [CVE-2025-67038]
---

Lantronix의 산업용 네트워크 기기 **EDS5000**에서 username 매개변수에 OS 명령을 주입할 수 있는 취약점이 발견됐다. 주입된 명령은 root 권한으로 실행되며 CISA KEV에 등재되어 실제 악용이 확인됐다.

## 타임라인

- 2026-06-23 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2025-67038) — CVE-2025-67038 코드 인젝션 취약점 등재, username 매개변수 입력 검증 부재로 root 권한 명령 실행 가능

## 관련

[[ics-vulnerabilities]]
