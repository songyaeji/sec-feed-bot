---
slug: use-after-free-rce
first_seen: 2026-11-10
tags: [메모리안전, 사용후해제, 원격코드실행]
cves: [CVE-2026-55335]
---

# Use-after-free 취약점 — 원격코드실행

로직 오류로 인한 use-after-free 취약점. 여러 위치에서 발생하며 추가 권한 없이 원격 코드 실행 가능. 사용자 상호작용 불필요(CVSS 9.8).

## 타임라인

- 2026-11-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-55335) — CVE-2026-55335 use-after-free CVSS 9.8 RCE
