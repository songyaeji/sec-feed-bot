---
slug: linux-netdevsim-uninit
first_seen: 2026-06-24
tags: [시뮬레이터, 초기화오류, KMSAN]
cves: [CVE-2026-52985]
---

Linux netdevsim 네트워크 디바이스 시뮬레이터에서 nsim_dev_trap_skb_build()의 더미 skb_buff IP 헤더 구조체 초기화 누락. skb_put()으로 미초기화 메모리 할당하면 KMSAN이 초기화 안 된 값 검출. skb_put_zero() 사용으로 0 초기화 필요.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52985) — netdevsim iphdr 초기화 오류 공개

## 관련
