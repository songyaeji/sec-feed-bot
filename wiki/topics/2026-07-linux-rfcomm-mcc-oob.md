---
slug: linux-rfcomm-mcc-oob
first_seen: 2026-07-08
tags: [Linux, Bluetooth, 범위초과]
cves: [CVE-2026-53254]
---

Linux 커널 Bluetooth RFCOMM(Serial Port Profile의 다중화 프로토콜) MCC(Multiplexer Control Channel) 핸들러에서 skb 길이 검증 부재. MCC 핸들러가 skb->data를 프로토콜별 구조체로 직접 캐스팅하면서 skb->len 검사를 선행하지 않음. 원격 Bluetooth 장치가 잘못된 MCC 프레임 전송 시 **범위 초과 읽기** 발생.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53254) — CVE-2026-53254 공개 (CVSS 8.1)

## 관련

[[linux-l2cap-lock-race]]
