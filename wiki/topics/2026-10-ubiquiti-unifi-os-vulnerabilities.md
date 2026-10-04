---
slug: ubiquiti-unifi-os-vulnerabilities
first_seen: 2026-06-23
tags: [Network Management, Command Injection, Access Control]
cves: [CVE-2026-34910, CVE-2026-34909, CVE-2026-34908]
---

Ubiquiti의 네트워크 관리 플랫폼 **UniFi OS**에서 3개의 심각한 취약점이 발견됐다. 네트워크 접근 공격자가 임의 명령을 주입하거나, 파일에 접근하거나, 시스템 설정을 변경할 수 있으며 모두 CISA KEV에 등재되어 실제 악용이 확인됐다.

## 타임라인

- 2026-06-23 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-34910) — CVE-2026-34910 명령 인젝션, 네트워크 접근 공격자가 명령 주입 가능
- 2026-06-23 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-34909) — CVE-2026-34909 경로 순회, 네트워크 접근으로 시스템 파일 접근 및 계정 조작 가능
- 2026-06-23 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-34908) — CVE-2026-34908 접근 제어 우회, 네트워크 접근으로 시스템 설정 무단 변경

## 관련

[[network-device-vulnerabilities]]
