---
slug: linux-l2cap-lock-race
first_seen: 2026-07-08
tags: [Linux, Bluetooth, 동시성]
cves: [CVE-2026-53071]
---

Linux 커널 Bluetooth L2CAP 구현에서 `l2cap_ecred_reconf_rsp()` 함수가 `l2cap_chan_lock` 없이 `l2cap_chan_del()` 호출. 다중 스레드 환경에서 경합 조건으로 메모리 손상 가능(CVSS 8.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53071) — CVE-2026-53071 공개 (CVSS 8.8)

## 관련
