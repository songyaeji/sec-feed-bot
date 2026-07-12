---
slug: linux-wireguard-napi
first_seen: 2026-07-10
tags: [커널버그, 네트워킹, WireGuard]
cves: [CVE-2026-52945]
---

Linux 커널 WireGuard의 threaded NAPI 활성화 관련 취약점. 프로덕션 사용 중 드문 경우이지만 심각한 문제 확인: 특정 WireGuard 피어의 복호화 측 완전 정지(성능 저하 없음, 복구 불가). MAX_QUEUED_PACKETS(1024 skbs) 도달 및 wg_packet_rx_poll() 호출 중단. 복호화만 영향받음. (CVSS 7.5)

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52945) — Linux WireGuard 패치 공개

## 관련
