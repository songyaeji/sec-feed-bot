---
slug: linux-iommu-vt-d-pasid-race
first_seen: 2026-05-27
tags: [리눅스커널, IOMMU, 메모리관리]
cves: [CVE-2026-45945]
---

Linux 커널 drivers/iommu/vt-d에서 PASID(Process Address Space ID) 테이블 엔트리 교체 시 발생하는 경합 조건. 512비트 엔트리를 단일 구조체 할당으로 업데이트하는데 IOMMU 하드웨어가 128비트씩 여러 청크로 페칭하면서 중간에 불완전한 상태를 관찰할 수 있음. Present 비트가 설정된 상태에서의 엔트리 교체는 일관성 없는 상태 야기. clear-then-update 흐름으로 수정됨.

## 타임라인

- 2026-05-27 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-45945) — CVE-2026-45945 공개 및 커널 패치 적용

## 관련

[[linux-iommu-domain-nofail]]
[[linux-iommu-vt-d-oops]]
