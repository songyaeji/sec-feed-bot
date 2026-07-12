---
slug: linux-netfilter-osf-option
first_seen: 2026-07-10
tags: [커널버그, 범위초과, Netfilter]
cves: [CVE-2026-52999]
---

Linux 커널 netfilter nfnetlink_osf의 TCP 옵션 파싱 범위 초과 취약점. `nf_osf_match()` 함수가 공유 컨텍스트의 옵션 포인터를 진전시키되, 일치 시 복구 안 함. 다음 핑거프린트 체크에서 옵션 버퍼 끝에서 시작되어 가비지 데이터 읽음. (CVSS 9.1)

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52999) — Linux netfilter OSF 패치 공개

## 관련
