---
slug: linux-fcntl-softirq-deadlock
first_seen: 2026-06-24
tags: [커널버그, 데드락, 신호처리]
cves: [CVE-2026-52946]
---

Linux 커널 fs/fcntl의 `send_sigio()` 및 `send_sigurg()` 함수에서 SOFTIRQ 안전성 위반으로 인한 데드락. 프로세스 그룹 신호 처리 중 input_inject_event 또는 TCP_URG 수신으로 트리거되는 소프트IRQ에서 tasklist_lock 읽기 잠금을 획득할 때 발생. RCU 기반 순회로 변경되어 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52946) — Linux 커널 fcntl 패치 공개

## 관련
