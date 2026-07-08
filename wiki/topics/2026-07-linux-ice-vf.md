---
slug: linux-ice-vf
first_seen: 2026-07-08
tags: [Linux kernel, 네트워크 드라이버, NULL 포인터]
cves: [CVE-2026-53289]
---

Linux 커널 ice 네트워크 드라이버의 ice_reset_all_vfs() 함수에서 발생하는 NULL 포인터 역참조. ice_vf_rebuild_vsi() 호출 실패 시 반환값 검사 없이 계속 진행되어 VSI 재구성 실패 중 (예: NVM 펌웨어 업데이트) 메모리 접근 위반 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53289) — CVE-2026-53289 공개 (CVSS 5.5)
