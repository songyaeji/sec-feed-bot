---
slug: linux-amdkfd-sdma-overflow
first_seen: 2026-07-08
tags: [Linux, AMD, GPU]
cves: [CVE-2026-53143]
---

Linux 커널 amdkfd(AMD KFD) 드라이버 GFX11 칩셋의 **SDMA**(System Direct Memory Access) 큐 체크포인트/복구에서 구조체 크기 오류로 인한 **버퍼 오버플로우**. CP-compute 변형을 KFD_MQD_TYPE_SDMA 큐에 잘못 할당.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53143) — CVE-2026-53143: SDMA 큐 버퍼 오버플로우 (CVSS 7.8)

## 관련
