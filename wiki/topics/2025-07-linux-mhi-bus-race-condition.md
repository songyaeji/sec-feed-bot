---
slug: linux-mhi-bus-race-condition
first_seen: 2025-07-25
tags: [경쟁조건, 버스드라이버, 메모리손상]
cves: [CVE-2025-38429]
---

Linux 커널 MHI(Modem Host Interface) 버스 드라이버의 mhi_ep_ring_add_element 함수에서 읽기 포인터(rd_offset)를 버퍼 쓰기 전에 업데이트해 경쟁 조건으로 인한 메모리 손상이 발생한다.

## 타임라인

- 2025-07-25 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-38429) — rd_offset 업데이트 순서 변경으로 버퍼 쓰기 완료 후 업데이트하도록 패치

## 관련

없음
