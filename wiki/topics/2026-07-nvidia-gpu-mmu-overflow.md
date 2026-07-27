---
slug: nvidia-gpu-mmu-overflow
first_seen: 2026-07-27
tags: [NVIDIA, GPU, 정수오버플로우, 메모리접근]
cves: [CVE-2026-16280]
---

NVIDIA GPU의 물리 메모리 매핑(PMR) 오프셋 계산에서 4GB 이상 대형 PMR에 대해 32비트 주소 절단 문제 발생. 이로 인한 GPU MMU 매핑 오류로 비특권 사용자가 의도하지 않은 물리 메모리에 접근해 메모리 손상이나 정보 유출을 초래할 수 있다. CVSS 9.8로 평가됨.

## 타임라인

- 2026-07-24 — 취약점 발견
- 2026-07-27 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16280) — CVE-2026-16280 공개
