---
slug: linux-psi-race
first_seen: 2026-06-24
tags: [PSI지표, 경합조건, cgroup]
cves: [CVE-2026-52991]
---

Linux PSI(Pressure Stall Information) cgroup 파일 릴리스와 pressure write 간 경합 조건. cgroup_rmdir() 중 cgroup_file_release()가 of->priv 포인터 kfree하지만 pressure_write()의 ctx 접근이 cgroup_mutex 완전히 보호하지 않아 UAF 발생. CPU 간 경합으로 해제 후 ctx 참조 가능.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52991) — psi 파일 릴리스 경합 조건 공개

## 관련
