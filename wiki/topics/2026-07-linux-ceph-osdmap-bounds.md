---
slug: linux-ceph-osdmap-bounds
first_seen: 2026-07-10
tags: [커널버그, 범위초과, Ceph]
cves: [CVE-2026-52958]
---

Linux 커널 libceph의 `osdmap_decode()` 함수에서 범위 초과 접근 취약점. 손상된 osdmap 메시지에서 max_osd 값이 실제 내용을 초과할 경우 범위 초과 메모리 접근 발생 가능. osd_weight 디코딩 시 `ceph_decode_need()` 체크가 max_osd 반복을 고려하지 않음. (CVSS 9.1)

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52958) — Linux ceph 패치 공개

## 관련
