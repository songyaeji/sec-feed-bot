---
slug: linux-amdgpu-gds-init
first_seen: 2026-07-08
tags: [Linux, AMD, GPU]
cves: [CVE-2026-46276]
---

Linux 커널 **amdgpu** 드라이버에서 RDNA4(GFX 12) 칩셋의 **GDS**(Graphics Data Storage), GWS, OA 온칩 메모리 초기화 오류. RDNA4는 이들 자원을 제거했으나 초기화 코드가 불완전해 메모리 손상 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46276) — CVE-2026-46276: RDNA4 GDS 초기화 (CVSS 5.5)

## 관련
