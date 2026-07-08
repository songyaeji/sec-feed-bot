---
slug: rti-connext-vulnerabilities
first_seen: 2026-07-08
tags: [RTI, DDS, 메모리 안전]
cves: [CVE-2026-30803, CVE-2026-3894, CVE-2026-30802, CVE-2026-30799, CVE-2026-2467, CVE-2026-2674]
---

**RTI Connext** DDS 미들웨어의 핵심 라이브러리에서 메모리 안전 취약점. Connext Micro 버전에서 정수 언더플로우로 인한 버퍼 오버리드(CVE-2026-30803, CVSS 9.1), Connext Professional에서 범위 초과 읽기(CVE-2026-3894, CVSS 9.1), Connext Micro에서 범위 초과 읽기(CVE-2026-30802, CVSS 8.2). 정보 유출 및 DoS 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-30803) — CVE-2026-30803: Micro 정수 언더플로우 (CVSS 9.1)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-3894) — CVE-2026-3894: Professional 범위 초과 읽기 (CVSS 9.1)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-30802) — CVE-2026-30802: Micro 범위 초과 읽기 (CVSS 8.2)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-30799) — CVE-2026-30799: Professional 미인증 기능 ID 스푸핑 (CVSS 8.1)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-2467) — CVE-2026-2467: Professional 힙 버퍼 오버플로우 (CVSS 8.1)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-2674) — CVE-2026-2674: Professional/Queueing 범위 초과 쓰기 (CVSS 8.1)

## 관련
