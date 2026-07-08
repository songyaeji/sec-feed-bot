---
slug: linux-xsk-toctou
first_seen: 2026-07-08
tags: [Linux, 커널, 경합상태]
cves: [CVE-2026-53250]
---

Linux 커널의 **xsk**(XDP 소켓) 메타데이터 처리에서 검사-사용-폐기(TOCTOU) 취약점이 발견됐다. xsk_skb_metadata()가 UMEM 버퍼에서 csum_start와 csum_offset을 읽을 때, 사용자 공간에서 동시에 수정하면서 경합 상태가 발생한다(CVSS 7.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53250) — CVE-2026-53250 공개

## 관련
