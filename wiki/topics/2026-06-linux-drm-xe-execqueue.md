---
slug: linux-drm-xe-execqueue
first_seen: 2026-06-24
tags: [GPU드라이버, 메모리안전, 오류처리]
cves: [CVE-2026-52976]
---

Intel Xe GPU 드라이버의 xe_exec_queue_create_ioctl()에서 오류 처리 경로의 자원 정리 누락 발생. hw_engine_group_add 실패 시 VM 컴퓨트 큐 리스트에서 제거하지 않거나, xa_alloc 실패 시 hw_engine_group에서 제거하지 않아 사용 후 해제 가능.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52976) — drm/xe exec_queue 정리 오류 공개

## 관련
