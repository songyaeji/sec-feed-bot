---
slug: linux-drm-ttm-shrink-lru
first_seen: 2026-06-24
tags: [GPU버그, 데드락, 메모리관리]
cves: [CVE-2026-52949]
---

Linux 커널 drm/ttm의 `ttm_bo_shrink()` 함수에서 백업 실패 시 발생하는 무한 LRU 순회 데드락. 백업 실패 후 bulk_move 제거 및 LRU 꼬리 이동이 리스트 순회 커서 앞에 리소스를 배치하여 루프를 일으킴. bulk_move 제거를 성공 경로로만 이동하고 unevictable 여부 확인 추가로 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52949) — Linux drm/ttm 패치 공개

## 관련

[[linux-drm-ttm-swapout-lru]]
