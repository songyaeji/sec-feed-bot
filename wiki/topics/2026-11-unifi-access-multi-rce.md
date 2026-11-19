---
slug: unifi-access-multi-rce
first_seen: 2026-11-19
tags: [TOCTOU, SQL인젝션, RCE, 접근제어, 권상향]
cves: [CVE-2026-132802, CVE-2026-132803]
---

Ubiquiti **UniFi Access** 애플리케이션에서 2개의 중대 취약점이 발견됐다. 심볼릭 링크 해석 미검증으로 인한 TOCTOU(Time-of-Check-Time-of-Use) 취약점(CVSS 9.9)으로 네트워크 접근 및 저권한 사용자가 root 권한 코드 실행이 가능하고, 인증된 SQL 인젝션(CVSS 9.9) 취약점으로 권한 상향이 가능하다.

## 타임라인

- 2026-11-19 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-132802) — CVE-2026-132802 (CVSS 9.9) UniFi Access 심볼릭 링크 해석 미검증 TOCTOU 취약점, 네트워크 접근·저권한 사용자 root 권한 코드 실행 가능
- 2026-11-19 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-132803) — CVE-2026-132803 (CVSS 9.9) UniFi Access 인증된 SQL 인젝션 다중 취약점, 호스트 기기 권한 상향 가능

## 관련
