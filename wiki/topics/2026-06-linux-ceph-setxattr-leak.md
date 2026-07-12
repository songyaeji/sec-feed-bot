---
slug: linux-ceph-setxattr-leak
first_seen: 2026-06-24
tags: [메모리누수, Ceph, 커널버그]
cves: [CVE-2026-52962]
---

Linux 커널 fs/ceph의 `__ceph_setxattr()` 함수에서 메모리 누수 취약점. 재시도 루프 중 old_blob이 ci->i_xattrs.prealloc_blob 값을 저장하지만 ceph_buffer_put() 호출 누락으로 인해 메모리 누수 발생. old_blob에 대한 ceph_buffer_put() 호출 추가로 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52962) — Linux Ceph 패치 공개

## 관련

[[linux-ceph-xattr-blob-bug]]
