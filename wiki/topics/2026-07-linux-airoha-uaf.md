---
slug: linux-airoha-uaf
first_seen: 2026-07-07
tags: [Linux kernel, network driver, use-after-free, RCE]
cves: [CVE-2026-53248]
---

Linux 커널 Airoha 이더넷 드라이버의 메타데이터 dst 해제 후 사용(UAF) 취약점. airoha_metadata_dst_free()에서 RCU 그레이스 기간 없이 즉시 kfree()하여 RX 경로의 skb_dst_set_noref()에서 해제된 메모리 접근 가능. 커널 권한 코드 실행 위협.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53248) — CVE-2026-53248 공개 (CVSS 8.8)
