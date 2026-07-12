---
slug: linux-iommu-domain-nofail
first_seen: 2026-06-24
tags: [커널버그, IOMMU, 메모리안전]
cves: [CVE-2026-52952]
---

Linux 커널 drivers/iommu의 `__iommu_group_set_domain_nofail()` 함수에서 복구 중인 장치 거부 검사가 nofail 경로까지 적용되어 발생하는 WARN_ON 및 사용 후 해제. IOMMU_SET_DOMAIN_MUST_SUCCEED 플래그를 처리하여 group->recovery_cnt 펜스를 우회하고, 대신 개별 장치 차단 확인을 추가하여 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52952) — Linux iommu 패치 공개

## 관련

[[linux-iommu-vt-d-oops]]
