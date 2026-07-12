---
slug: linux-futex-requeue-deadlock
first_seen: 2026-06-24
tags: [동기화원시, 데드락, 신호처리]
cves: [CVE-2026-52977]
---

Linux futex requeue-PI 작업 중 신호/타임아웃으로 인한 데드락 발생. task A가 대기-리큐 타임아웃 후 Q_REQUEUE_PI_IGNORE 상태를 설정하지만 하시 락 대기 중이고, task B가 우선순위 높아 task A가 wake-up 이전에 다시 락 획득 시 데드락.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52977) — futex 신호/타임아웃 데드락 공개

## 관련
