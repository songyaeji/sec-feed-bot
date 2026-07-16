---
slug: pegatron-tdelo64-privesc
first_seen: 2026-07-15
tags: [Pegatron, 드라이버, 하드웨어I/O, 권한상향]
cves: [CVE-2026-14960]
---

**Pegatron Tdelo64.sys** 드라이버가 `\\\\.\\TdeIo` 디바이스 인터페이스를 통해 권한 검증 없이 하드웨어 I/O 포트 읽기·쓰기 기능(TDE_IOCTL_INDEXIO_READ/WRITE IOCTL)을 노출한다. 일반 사용자가 임의 하드웨어 레지스터 조작, 펌웨어 인터페이스 변조, 시스템 불안정화 또는 저수준 지속성 확보 가능(CVSS 9.8).

## 타임라인

- 2026-07-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14960) — CVE-2026-14960 공개
