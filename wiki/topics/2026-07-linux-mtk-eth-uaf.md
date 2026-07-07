---
slug: linux-mtk-eth-uaf
first_seen: 2026-07-07
tags: [Linux kernel, use-after-free, network driver, RCE]
cves: [CVE-2026-53247]
---

Linux 커널 MediaTek 이더넷 드라이버(mtk_eth_soc)의 해제 후 사용(UAF) 취약점. mtk_free_dev()에서 metadata_dst를 RCU 그레이스 기간 없이 즉시 kfree()하여 RX 경로에서 해제된 메모리 접근 가능. 커널 권한 코드 실행 위협.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53247) — CVE-2026-53247 공개 (CVSS 9.8)
