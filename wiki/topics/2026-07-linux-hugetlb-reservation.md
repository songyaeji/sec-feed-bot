---
slug: linux-hugetlb-reservation
first_seen: 2026-07-07
tags: [Linux kernel, memory management]
cves: [CVE-2026-53154]
---

Linux 커널 대용량 메모리 페이지(hugetlb) 복사 경로에서 오류 발생 시 VMA 예약 복구 실패. alloc_hugetlb_folio()이 예약을 소비한 후 copy_user_large_folio()에서 실패해도 예약을 복구하지 않아 메모리 누수 발생.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53154) — CVE-2026-53154 공개 (CVSS 5.5)
