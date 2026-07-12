---
slug: linux-airoha-bql
first_seen: 2026-06-24
tags: [네트워크드라이버, 큐관리, BQL]
cves: [CVE-2026-52983]
---

Linux Airoha 이더넷 드라이버의 TX 경로 BQL(Byte Queue Limits) 불균형. airoha_dev_xmit()에서 인플라이트 패킷은 AIROHA_NUM_TX_RING 큐로만 계정하지만, airoha_qdma_tx_napi_poll()의 완료 처리는 모든 netdev TX 큐로 계정해 BQL 불일치.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52983) — airoha BQL 불균형 공개

## 관련
