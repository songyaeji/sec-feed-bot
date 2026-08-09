---
slug: msi-axe6600-command-injection
first_seen: 2026-08-09
tags: [라우터, 명령주입, RCE]
cves: [CVE-2026-71986, CVE-2026-71987, CVE-2026-71988, CVE-2026-71989, CVE-2026-71990, CVE-2026-71991, CVE-2026-71992]
---

MSI Radix AXE6600 라우터 펌웨어 v781521에서 dmz·alg·portFw 등 8개 함수의 명령 주입 취약점이 발견됐다. 모두 CVSS 9.8 심각도로, 원격 공격자가 인증 없이 라우터에 접근해 임의 명령을 실행하고 루트 권한을 획득할 수 있다.

## 타임라인

- 2026-08-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71986) — MSI Radix AXE6600 v781521 8개 함수 명령 주입 취약점 공개 (dmz·alg·portFw·porTrigger·TelnetSSH·macfilter)
