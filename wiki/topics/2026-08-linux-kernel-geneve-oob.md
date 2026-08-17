---
slug: linux-kernel-geneve-oob
first_seen: 2026-08-15
tags: [커널, geneve, GRO, 버퍼오버플로우]
cves: [CVE-2026-72407, CVE-2026-72408]
---

# Linux 커널 — Geneve GRO 최적화 경계 초과 읽기

Linux 커널의 **geneve GRO(Generic Receive Offload)** 구현에서 내부 네트워크 오프셋 검증 누락 및 클라이언트-서버 간 상태 불일치로 인한 경계 초과 읽기. 패치로 고정됨.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-72407) — CVE-2026-72407 geneve_gro_complete 오프셋 검증 누락
- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-72408) — CVE-2026-72408 geneve_gro_hint 게이트 미적용 KASAN 버그
