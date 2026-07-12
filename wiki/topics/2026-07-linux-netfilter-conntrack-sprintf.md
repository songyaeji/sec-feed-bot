---
slug: linux-netfilter-conntrack-sprintf
first_seen: 2026-07-10
tags: [커널버그, 버퍼오버플로우, Netfilter]
cves: [CVE-2026-53002]
---

Linux 커널 netfilter conntrack의 스택 버퍼 오버플로우. `mangle_content_len()` 함수에서 `sprintf()` 사용으로 경계 검사 부재. SDP 세션 파싱 시 버퍼 크기 초과 쓰기 발생. (CVSS 9.8)

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53002) — Linux netfilter conntrack 패치 공개

## 관련
