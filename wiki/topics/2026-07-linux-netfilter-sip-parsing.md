---
slug: linux-netfilter-sip-parsing
first_seen: 2026-07-10
tags: [커널버그, 포트파싱, Netfilter]
cves: [CVE-2026-52986]
---

Linux 커널 netfilter nf_conntrack_sip의 포트 파싱 취약점. `simple_strtoul()` 사용으로 NUL 종료 문자 가정 문제. `epaddr_len()`, `ct_sip_parse_header_uri()`, `ct_sip_parse_request()`에서 경계 검사 없이 포인터 역참조. SIP 패킷 파싱 시 범위 초과 접근 발생 가능. (CVSS 9.8)

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52986) — Linux netfilter SIP 패치 공개

## 관련
