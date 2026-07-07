---
slug: linux-netfilter-mac-validation
first_seen: 2026-07-07
tags: [Linux kernel, DoS]
cves: [CVE-2026-52942]
---

Linux 커널 netfilter 로깅 기능의 MAC 헤더 검증 누락 취약점. 로그 출력 경로에서 MAC 헤더 설정 여부를 확인하지 않아 NULL 포인터 역참조 발생 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52942) — CVE-2026-52942 공개 (CVSS 7.1)
