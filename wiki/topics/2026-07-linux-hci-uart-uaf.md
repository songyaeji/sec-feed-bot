---
slug: linux-hci-uart-uaf
first_seen: 2026-07-08
tags: [Linux, Bluetooth, UAF]
cves: [CVE-2026-46275]
---

Linux 커널 **hci_uart** Bluetooth UART 드라이버 생명주기 관리에서 **사용 후 해제(UAF)** 및 NULL 포인터 역참조 취약점. 종료 및 초기화 경로의 동시성 문제로 메모리 오염.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46275) — CVE-2026-46275: Bluetooth hci_uart UAF (CVSS 7.8)

## 관련
