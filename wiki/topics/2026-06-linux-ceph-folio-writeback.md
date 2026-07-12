---
slug: linux-ceph-folio-writeback
first_seen: 2026-06-24
tags: [메모리누수, Ceph, 커널버그]
cves: [CVE-2026-52960]
---

Linux 커널 fs/ceph의 쓰기 배치(folio batch)에서 쓰기 불가능한 포일리오 참조 누수. filemap_get_folios로 획득한 포일리오는 참조 카운트를 유지하는데, 배치에서 제거된 포일리오가 folio_put() 호출 없이 버려져 메모리 누수 발생. folio_put() 호출 추가로 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52960) — Linux Ceph 패치 공개

## 관련
