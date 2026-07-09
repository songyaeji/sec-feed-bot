---
slug: tenda-ac7-rce
first_seen: 2026-06-19
tags: [Tenda, 버퍼오버플로우, RCE, 라우터]
cves: [CVE-2026-51843, CVE-2026-51844, CVE-2026-51845, CVE-2026-51846]
---

Tenda AC7 v15.03.06.44 펌웨어의 `/goform/AdvSetMacMtuWan` 인터페이스에서 4개의 스택 버퍼 오버플로우 취약점. wanMTU, cloneType, mac, wanSpeed 파라미터에서 모두 CVSS 9.8로 원격 코드 실행 가능.

## 타임라인

- 2026-06-19 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-51843) — CVE-2026-51843 (CVSS 9.8) wanMTU 스택 버퍼 오버플로우
- 2026-06-19 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-51844) — CVE-2026-51844 (CVSS 9.8) cloneType 스택 버퍼 오버플로우
- 2026-06-19 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-51845) — CVE-2026-51845 (CVSS 9.8) mac 스택 버퍼 오버플로우
- 2026-06-19 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-51846) — CVE-2026-51846 (CVSS 9.8) wanSpeed 스택 버퍼 오버플로우
