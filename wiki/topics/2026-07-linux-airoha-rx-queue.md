---
slug: linux-airoha-rx-queue
first_seen: 2026-07-08
tags: [Linux kernel, 네트워크 드라이버, 초기화 순서]
cves: [CVE-2026-53298]
---

Linux 커널 net/airoha 드라이버의 airoha_qdma_init_rx_queue() 함수에서 발생하는 초기화 순서 오류. 큐 항목 또는 DMA 디스크립터 목록 할당 실패 시 ndesc 변수가 아직 초기화되지 않은 상태에서 airoha_qdma_cleanup()이 호출되어 NULL 포인터 역참조 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53298) — CVE-2026-53298 공개 (CVSS 5.5)
