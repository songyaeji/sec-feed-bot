---
slug: linux-qrtr-refcount-uaf
first_seen: 2026-06-24
tags: [커널버그, 참조카운트, 경합조건]
cves: [CVE-2026-52947]
---

Linux 커널 net/qrtr의 `qrtr_port_remove()` 함수에서 RCU 업데이트 패러다임 위반으로 인한 참조 카운트 포화 및 사용 후 해제. 포트 XArray 제거 전에 소켓 참조 카운트를 감소시켜 RCU 리더가 이미 0인 소켓에 `sock_hold()`를 시도할 수 있음. 참조 카운트 감소를 xa_erase 및 synchronize_rcu 완료 후로 이동하여 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52947) — Linux 커널 qrtr 패치 공개

## 관련
