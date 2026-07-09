---
slug: netty-ipv6-subnet-bypass
first_seen: 2026-06-11
tags: [Netty, 네트워크, IPv6, 서브넷, ACL]
cves: [CVE-2026-44249]
---

# Netty IPv6 서브넷 규칙 우회 취약점

**Netty** netty-handler v4.1.135.Final, v4.2.15.Final 이전 버전에서 IpSubnetFilterRule.compareTo()의 잘못된 마스킹 연산으로 인해 IPv6 서브넷 규칙 우회 가능. 유효한 공개 IP 주소가 필터 규칙을 우회할 수 있음. **CVSS 8.1**.

## 타임라인

- 2026-06-11 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44249) — CVE-2026-44249 공개 (CVSS 8.1)
