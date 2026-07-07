---
slug: linux-skbuff-zerocopy-ref
first_seen: 2026-07-07
tags: [Linux kernel, memory safety]
cves: [CVE-2026-52943]
---

Linux 커널 네트워크 스택의 패킷 분할 함수(pskb_carve)에서 제로카피 참조 정보 누락. memcpy로 기존 skb_shared_info를 복사할 때 destructor 관련 상태가 불완전해 메모리 손상 발생 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52943) — CVE-2026-52943 공개 (CVSS 7.8)
