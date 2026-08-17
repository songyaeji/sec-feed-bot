---
slug: linux-kernel-ipv4-fib
first_seen: 2026-08-15
tags: [커널, 라우팅, IPv4, 정책]
cves: [CVE-2026-72421]
---

# Linux 커널 — IPv4 FIB 에러 라우트 무시 오류

Linux 커널의 **CONFIG_IP_MULTIPLE_TABLES** 활성화 후 규칙이 없을 때 fib_lookup() 함수가 합병된 local/main 테이블에서 에러 라우트를 무시해 일관성 없는 동작 발생. 패치로 고정됨.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-72421) — CVE-2026-72421 IPv4 라우팅 일관성 결함
