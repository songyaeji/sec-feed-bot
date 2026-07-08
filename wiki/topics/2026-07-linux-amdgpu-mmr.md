---
slug: linux-amdgpu-mmr
first_seen: 2026-07-08
tags: [Linux kernel, 그래픽 드라이버, 동시성]
cves: [CVE-2026-53293]
---

Linux 커널 drm/amdgpu 드라이버의 AMDGPU_INFO_READ_MMR_REG ioctl 구현 결함. 리셋 세마포어와 mm_lock 간 잠금 순서 오류 및 잠금 유지 상태에서 copy_to_user() 호출로 인한 교착 상태(deadlock) 위험. 메모리 맵 레지스터 읽기 작업에서 동시성 문제 발생.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53293) — CVE-2026-53293 공개 (CVSS 5.5)
