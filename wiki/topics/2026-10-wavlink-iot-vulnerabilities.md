---
slug: wavlink-iot-vulnerabilities
first_seen: 2026-10-13
tags: [IoT카메라보안, 라우터보안, 버퍼오버플로우]
cves: [CVE-2026-109109, CVE-2026-109110]
---

Wavlink IP 카메라 및 무선 제품에서 CVSS 10.0의 다중 취약점이 발견됐다. 카메라의 스택 버퍼오버플로우와 데몬의 OS 명령 인젝션으로 미인증 원격 공격 가능하며 공개 exploit 존재한다.

## 타임라인

- 2026-10-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-109109) — CVE-2026-109109 WL-WN530BE1-A strcpy 버퍼오버플로우 공개 (CVSS 10.0)
- 2026-10-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-109110) — CVE-2026-109110 WL-WN592AX6 wmapd 명령 인젝션 공개 (CVSS 10.0)

## 관련

[[wavlink-buffer-overflow]]
