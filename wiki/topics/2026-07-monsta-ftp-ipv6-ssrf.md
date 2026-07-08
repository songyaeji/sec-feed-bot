---
slug: monsta-ftp-ipv6-ssrf
first_seen: 2026-07-08
tags: [SSRF, FTP]
cves: [CVE-2026-60105]
---

**Monsta FTP** 2.14.5 이전 버전의 `fetchRemoteFile` 액션에서 IP 블로킹 리스트 검사가 IPv4 주소 내장 IPv6 주소(예: `::ffff:127.0.0.1`)를 감지하지 못하여, 미인증 공격자가 SSRF로 로컬호스트/내부망 리소스에 접근할 수 있는 취약점.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-60105) — CVE-2026-60105 공개 (CVSS 8.6)
