---
slug: linux-phonet-rcu-grace
first_seen: 2026-07-07
tags: [Linux kernel, concurrency, RCU]
cves: [CVE-2026-53157]
---

Linux 커널 phonet 프로토콜 스택의 RCU(Read-Copy-Update) 그레이스 기간 위반. phonet_device_destroy()에서 list_del_rcu()로 장치를 리스트에서 제거하고 즉시 kfree()하여 RCU 읽기 중인 스레드가 해제된 메모리에 접근 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53157) — CVE-2026-53157 공개 (CVSS 7.8)
