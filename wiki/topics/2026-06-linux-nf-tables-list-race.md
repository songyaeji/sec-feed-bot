---
slug: linux-nf-tables-list-race
first_seen: 2026-06-24
tags: [netfilter, 경합조건, 룰셋업데이트]
cves: [CVE-2026-52988]
---

Linux netfilter nf_tables 룰 엔진에서 커밋 단계 중 후크 리스트 추가 시 RCU 안전성 부재. 동시 netlink dump 중 리스트 순회를 보호하지 않아 새 후크를 basechain/flowtable 리스트에 직접 추가 시 경합. splice_list_rcu()로 원자적 발행 필요.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52988) — nf_tables 후크 리스트 RCU 부재 공개

## 관련
