---
slug: linux-drm-ttm-swapout-lru
first_seen: 2026-06-24
tags: [GPU버그, 데드락, 메모리관리]
cves: [CVE-2026-52965]
---

Linux 커널 drm/ttm의 `ttm_bo_swapout()` 함수에서 스왑아웃 실패 후 복구 중 발생하는 무한 LRU 순회. ttm_resource_move_to_lru_tail이 리스트 순회 커서 앞에 리소스를 배치하여 다음 순회에서 동일 리소스 재검사. bulk_move 제거를 성공 경로로만 이동하고, unevictable 상태인 리소스도 제거 가능하도록 ttm_resource_del_bulk_move_unevictable() 추가로 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52965) — Linux drm/ttm 패치 공개

## 관련

[[linux-drm-ttm-shrink-lru]]
