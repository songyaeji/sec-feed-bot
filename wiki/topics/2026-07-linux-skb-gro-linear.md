---
slug: linux-skb-gro-linear
first_seen: 2026-07-08
tags: [Linux, 네트워크, 메모리 안전]
cves: [CVE-2026-53235]
---

Linux 커널 `skb_gro_receive_list()` 함수에서 `pskb_may_pull()` 없이 `skb_pull()` 호출. **GRO(Generic Receive Offload)** 프래그먼트 수신 시 `napi_gro_frags()` 경로를 통해 도착한 skb에서 데이터가 선형 영역(linear area)에 없으면 **범위 초과 접근** 또는 메모리 손상 발생.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53235) — CVE-2026-53235 공개 (CVSS 7.5)

## 관련
