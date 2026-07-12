---
slug: linux-tipc-double-free
first_seen: 2026-07-10
tags: [커널버그, 이중해제, TIPC]
cves: [CVE-2026-52993]
---

Linux 커널 TIPC 프로토콜 `tipc_buf_append()` 함수의 이중 해제 취약점. `tipc_msg_validate()` 함수가 skb을 재할당할 수 있지만, 검증 실패 시 로컬 변수 포인터를 통해 원본 skb을 해제(이미 해제됨). (CVSS 9.8)

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52993) — Linux TIPC 패치 공개

## 관련
