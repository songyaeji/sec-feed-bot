---
slug: linux-ceph-xattr-blob-bug
first_seen: 2026-06-24
tags: [커널버그, Ceph, 메타데이터]
cves: [CVE-2026-52961]
---

Linux 커널 fs/ceph의 `__ceph_build_xattrs_blob()` 함수에서 stale blob 크기로 인한 커널 BUG_ON 충돌. generic/642 테스트 케이스에서 재현되는 xattr blob 크기 불일치로 인한 어셜션 실패. Ceph 파일시스템 메타데이터 처리 중 손상된 상태 검출.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52961) — Linux Ceph 패치 공개

## 관련

[[linux-ceph-setxattr-leak]]
