---
slug: linux-neigh-xmit-ownership
first_seen: 2026-06-24
tags: [네트워킹, SKB관리, 메모리누수]
cves: [CVE-2026-52981]
---

Linux 이웃 테이블 전송 함수 neigh_xmit()에서 초기화되지 않은 이웃 테이블 발견 시(예: IPv6 비활성화) SKB 해제하지 않는 메모리 누수. 대부분의 코드 경로는 SKB 전송 또는 해제하지만 EAFNOSUPPORT 반환 경로에서는 out_kfree_skb 스킵. mpls 등 사용자가 반환값 무시 시 누수 가능.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52981) — neigh_xmit SKB 소유권 누수 공개

## 관련
