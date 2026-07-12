---
slug: linux-bonding-3ad-race
first_seen: 2026-06-24
tags: [네트워킹, 경합조건, 리ンク어그리게이션]
cves: [CVE-2026-52975]
---

Linux bonding 드라이버의 802.3ad 링크 어그리게이션 구현에서 port->aggregator 포인터의 RCU 규칙 부재로 인한 데이터 경합 발생. bond_3ad_state_machine_handler()와 bond_3ad_get_active_agg_info() 간 동시 접근 시 경합 조건 가능.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52975) — bonding 3ad 데이터 경합 조건 공개

## 관련
