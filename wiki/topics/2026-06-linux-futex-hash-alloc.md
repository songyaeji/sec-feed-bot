---
slug: linux-futex-hash-alloc
first_seen: 2026-06-24
tags: [Linux, futex, 스레드, 메모리]
cves: [CVE-2026-52973]
---

# Linux futex 기본 해시 할당 문제

Linux 커널 futex 메커니즘에서 need_futex_hash_allocate_default()가 엄격한 pthread 의미론에 의존하면서 CLONE_THREAD를 남용하여 비동시성 가정을 위반할 수 있는 취약점. **CVSS 7.8**.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52973) — CVE-2026-52973 공개 (CVSS 7.8)
