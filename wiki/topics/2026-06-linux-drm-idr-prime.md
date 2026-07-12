---
slug: linux-drm-idr-prime
first_seen: 2026-06-24
tags: [커널버그, GPU, 메모리관리]
cves: [CVE-2026-52966]
---

Linux 커널 drivers/gpu의 `drm_prime` DMA-buf 핸들 변경 로직에서 새 IDR 포인터를 기존 포인터 위치에 올바르게 교체하지 않는 논리 오류. 커밋 5e28b7b94408에서 도입된 버그로 IDR 객체 포인터 교체 실패로 데이터 손상 및 메모리 누수 야기. rbdma_bufs 비트맵 검증 관련 syzbot 경고 발생.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52966) — Linux drm 패치 공개

## 관련
