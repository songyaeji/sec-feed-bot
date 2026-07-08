---
slug: linux-airoha-tx-init
first_seen: 2026-07-08
tags: [Linux kernel, 네트워크 드라이버, 초기화 순서]
cves: [CVE-2026-53299]
---

Linux 커널 net/airoha 드라이버의 airoha_qdma_init_tx() 함수에서 발생하는 초기화 순서 오류. 큐 항목 목록 할당 실패 시 airoha_qdma_cleanup_tx_queue()에서 초기화되지 않은 ndesc를 사용하여 NULL 포인터 역참조 발생 가능. RX 초기화와 유사한 패턴의 메모리 안전성 결함.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53299) — CVE-2026-53299 공개 (CVSS 5.5)
