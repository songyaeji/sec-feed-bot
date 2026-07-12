---
slug: linux-kvm-s390-gait-oob
first_seen: 2026-06-24
tags: [kvm, 하이퍼바이저, 메모리안전]
cves: [CVE-2026-52968]
---

Linux KVM s390 플랫폼에서 PCI 추상 인터페이스 테이블(GAIT) 인덱싱 시 이중 스케일링으로 범위 초과 접근이 발생한다. struct zpci_gaite 포인터에 sizeof를 재적용하는 오류로 aisb >= 32 일 때 버퍼 오버플로우 가능.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52968) — KVM s390 PCI 추상화 계층 GAIT 테이블 이중 스케일링 버그 공개

## 관련
