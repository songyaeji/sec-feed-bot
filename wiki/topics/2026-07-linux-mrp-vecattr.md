---
slug: linux-mrp-vecattr
first_seen: 2026-07-07
tags: [Linux kernel, network, MRP protocol]
cves: [CVE-2026-53245]
---

Linux 커널 MRP(Multiple Registration Protocol) 구현의 벡터 속성 파싱 취약점. mrp_pdu_parse_vecattr()에서 valen(남은 이벤트 수) 감소 로직의 결함으로 인해 메모리 손상 발생 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53245) — CVE-2026-53245 공개 (CVSS 5.5)
