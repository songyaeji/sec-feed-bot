---
slug: linux-amdgpu-drm-exec
first_seen: 2026-06-24
tags: [GPU드라이버, 오류처리, 리소스정리]
cves: [CVE-2026-52987]
---

AMD GPU amdgpu 드라이버의 userq_vm_validate()에서 HMM 범위 반복 중 오류 발생 시 drm_exec_fini() 중복 호출. new_addition true일 때 범위 반복 전 fini 호출 후 오류 경로에서 재호출해 exec->objects 중복 해제 및 ww 컨텍스트 손상.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52987) — amdgpu drm_exec_fini 중복 호출 공개

## 관련
