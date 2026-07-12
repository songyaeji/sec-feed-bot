---
slug: linux-kvm-dirty-ring-oob
first_seen: 2026-06-24
tags: [kvm, 하이퍼바이저, 정수오버플로우]
cves: [CVE-2026-52969]
---

KVM dirty ring 백업 저장소(MAP_SHARED)의 오프셋 범위 검사에 u64 래핑 취약점 존재. kvm_reset_dirty_gfn()에서 코일링된 엔트리 오프셋(0xffffffffffffffc1)과 마스크로 합계가 0으로 우회되어 경계 검사를 통과, 영역 외 gfn 설정으로 권한상향 가능.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52969) — KVM dirty ring 오프셋 정수 래핑 오버플로우 공개

## 관련
