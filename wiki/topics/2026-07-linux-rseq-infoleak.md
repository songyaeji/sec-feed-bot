---
slug: linux-rseq-infoleak
first_seen: 2026-07-07
tags: [Linux kernel, concurrency, information leak]
cves: [CVE-2026-53243]
---

Linux 커널 rseq 서브시스템의 초기화되지 않은 스택 변수 정보 유출 취약점. rseq_exit_user_update()에서 스택 변수를 초기화하지 않은 채 사용하여 커널 메모리 정보 노출 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53243) — CVE-2026-53243 공개 (CVSS 5.5)
