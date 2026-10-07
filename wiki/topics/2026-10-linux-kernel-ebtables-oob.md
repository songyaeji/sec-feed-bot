---
slug: linux-kernel-ebtables-oob
first_seen: 2026-10-07
tags: [Linux, 커널취약점, 권한상향]
cves: [CVE-2026-53266]
---

Linux Kernel의 ebtables SNAT 타겟에서 ARP 송신자 하드웨어 주소 재작성 시 비선형 소켓 버퍼 단편의 경계를 초과해 쓸 수 있는 메모리 손상 취약점. 권한 없는 공격자가 이를 악용해 시스템 권한을 상향시키거나 서비스를 거부할 수 있다.

## 타임라인

- 2026-09-18 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-53266) — CVE-2026-53266 공개, ebtables SNAT 타겟 out-of-bounds write 취약점
