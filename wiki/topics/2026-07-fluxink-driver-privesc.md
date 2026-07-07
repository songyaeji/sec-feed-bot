---
slug: fluxink-driver-privesc
first_seen: 2026-07-07
tags: [Windows driver, privilege escalation, device driver]
cves: [CVE-2026-58583]
---

FluxInk(구 Sunia SPB Peripheral) 색상 관리 드라이버의 로컬 권한상향 취약점. TcnPeripheral64.sys 드라이버에서 \\Device\\PhysicalMemory를 통한 임의 물리 메모리 매핑 허용. 표준 사용자가 커널 메모리에 접근해 권한상향 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-58583) — CVE-2026-58583 공개, 1.0.7.6에서 수정 (CVSS 7.1)
