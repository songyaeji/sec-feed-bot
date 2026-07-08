---
slug: linux-ice-double-free
first_seen: 2026-07-08
tags: [Linux, 드라이버, 메모리 안전]
cves: [CVE-2026-53009]
---

Linux 커널의 **ice** 이더넷 드라이버에서 `ice_tso()` 또는 `ice_tx_csum()` 실패 시 오류 경로의 메모리 정리 누락으로 인한 이중 해제(double-free) 취약점(CVSS 7.8). 송신 버퍼(skb) 재사용 오류.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53009) — CVE-2026-53009 공개 (CVSS 7.8)

## 관련
