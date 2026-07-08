---
slug: linux-arm64-mapping
first_seen: 2026-07-08
tags: [Linux kernel, ARM64, 메모리 매핑]
cves: [CVE-2026-53288]
---

Linux 커널 ARM64의 초기 커널 매핑에서 발생하는 메모리 오버플로우. [data, end) 세그먼트의 마지막 부분이 init_pg_end[1]의 다음 페이지로 오버플로우되어 early_init_stack[2]의 간격 페이지에 침범할 수 있음. 초기 부팅 단계에서 스택 손상 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53288) — CVE-2026-53288 공개 (CVSS 5.5)
