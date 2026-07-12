---
slug: linux-iommu-vt-d-oops
first_seen: 2026-06-24
tags: [커널버그, IOMMU, 메모리접근]
cves: [CVE-2026-52953]
---

Linux 커널 drivers/iommu/vt-d의 `domain_remove_dev_pasid()` 함수에서 범위 외 메모리 접근 취약점. 정적 블로킹 도메인은 더미 도메인으로 dmar_domain 구조체가 없는데, 이 도메인에 접근할 때 범위를 벗어난 메모리 참조 발생. 항등 도메인처럼 조기 리턴하여 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52953) — Linux iommu/vt-d 패치 공개

## 관련

[[linux-iommu-domain-nofail]]
