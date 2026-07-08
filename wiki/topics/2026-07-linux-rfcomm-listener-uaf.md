---
slug: linux-rfcomm-listener-uaf
first_seen: 2026-07-08
tags: [Linux, Bluetooth, UAF]
cves: [CVE-2026-53256]
---

Linux 커널 Bluetooth RFCOMM 구현의 `rfcomm_connect_ind()` 함수에서 `rfcomm_get_sock_by_channel()`이 목록 잠금을 해제한 후 참조 카운트를 취하지 않고 리스너 소켓을 반환. **멀티스레드 환경**에서 반환된 소켓이 해제되고 난 후 사용되면서 **해제 후 사용(UAF)** 취약점 발생.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53256) — CVE-2026-53256 공개 (CVSS 8.0)

## 관련

[[linux-l2cap-lock-race]]
