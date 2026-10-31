---
slug: linux-nvme-tcp-memory-corruption
first_seen: 2025-04-01
tags: [메모리손상, NVMe, 프로토콜검증]
cves: [CVE-2025-21927]
---

Linux 커널 NVMe over TCP 드라이버의 nvme_tcp_recv_pdu 함수에서 헤더 길이 검증을 하지 않아 헤더 다이제스트 검증 중 할당된 메모리 범위를 벗어나 접근하는 메모리 손상이 발생한다.

## 타임라인

- 2025-04-01 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-21927) — 헤더 길이 검증 추가로 예상 범위를 벗어난 패킷 거부하도록 패치

## 관련

없음
