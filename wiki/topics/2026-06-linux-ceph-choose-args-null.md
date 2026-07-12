---
slug: linux-ceph-choose-args-null
first_seen: 2026-06-24
tags: [커널버그, Ceph, 서비스거부]
cves: [CVE-2026-52957]
---

Linux 커널 net/ceph의 `decode_choose_args()` 함수에서 NULL 버킷 포인터 역참조 취약점. OSD 맵의 CRUSH 맵에는 NULL 버킷이 존재할 수 있는데, choose_args 버킷 인덱스가 max_buckets 범위 체크만 수행하고 NULL 여부를 확인하지 않음. 버킷 유효성 확인(NULL 체크) 추가로 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52957) — Linux libceph 패치 공개

## 관련

[[linux-ceph-choose-args-rbtree]]
[[linux-ceph-x-decrypt-oob]]
