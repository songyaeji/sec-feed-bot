---
slug: linux-ceph-choose-args-rbtree
first_seen: 2026-06-24
tags: [커널버그, Ceph, 서비스거부]
cves: [CVE-2026-52954]
---

Linux 커널 net/ceph의 `decode_choose_args()` 함수에서 CRUSH 맵 choose_args 중복 인덱스 검사 부재로 인한 커널 BUG_ON. 손상된 OSD 맵 메시지가 같은 인덱스를 가진 두 개 이상의 choose_arg_map을 포함할 때 rbtree 삽입 어셜션 실패. 어셀션 대신 안전한 삽입 함수 사용 및 중복 메시지 거부로 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52954) — Linux libceph 패치 공개

## 관련

[[linux-ceph-choose-args-null]]
