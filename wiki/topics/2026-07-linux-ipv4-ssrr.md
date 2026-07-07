---
slug: linux-ipv4-ssrr
first_seen: 2026-07-07
tags: [Linux kernel, IPv4, IP options, privilege escalation]
cves: [CVE-2026-53249]
---

Linux 커널 IPv4 구현의 Loose Source and Record Route(LSRR)·Strict Source and Record Route(SSRR) IP 옵션 보안 강화. 해당 옵션 설정 권한을 CAP_NET_RAW로 제한하여 권한이 없는 사용자의 악용 방지.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53249) — CVE-2026-53249 공개 (CVSS 5.5)
