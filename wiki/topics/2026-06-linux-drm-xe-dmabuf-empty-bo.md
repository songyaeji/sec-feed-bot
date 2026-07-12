---
slug: linux-drm-xe-dmabuf-empty-bo
first_seen: 2026-06-24
tags: [GPU버그, 경합조건, 메모리안전]
cves: [CVE-2026-52951]
---

Linux 커널 drm/xe의 DMA-buf 첨부 단계가 bo 초기화 전에 시작되어 발생하는 경합조건. 수출자(예: amdgpu)의 invalidate_mappings 역호출이 불완전하거나 손상된 버퍼 객체에 접근하여 NULL 포인터 역참조 및 충돌 발생. DMA-buf 첨부를 완전 bo 초기화 후로 이동하여 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52951) — Linux drm/xe 패치 공개

## 관련

[[linux-drm-xe-dmabuf-retry-uaf]]
