---
slug: linux-drm-xe-dmabuf-retry-uaf
first_seen: 2026-06-24
tags: [GPU버그, UAF, 메모리안전]
cves: [CVE-2026-52950]
---

Linux 커널 drm/xe의 DMA-buf 초기화 루프에서 사용 후 해제 취약점. 재시도 루프 중 할당 및 초기화 과정에서 오류 발생 시 bo 메모리가 해제되지만 재시도 시도로 인해 사용 후 해제 발생 가능. 할당과 초기화 순서를 변경하여 안전한 재시도 구조로 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52950) — Linux drm/xe 패치 공개

## 관련

[[linux-drm-xe-dmabuf-empty-bo]]
