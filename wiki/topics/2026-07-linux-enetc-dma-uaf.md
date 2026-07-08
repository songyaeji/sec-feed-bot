---
slug: linux-enetc-dma-uaf
first_seen: 2026-07-08
tags: [Linux kernel, 네트워크 드라이버, DMA, 해제 후 사용]
cves: [CVE-2026-53300]
---

Linux 커널 net/enetc 드라이버의 NTMP DMA 사용 후 해제(use-after-free) 취약점. netc_xmit_ntmp_cmd() 타임아웃 시 반환 오류 처리 미흡으로 대기 중인 명령이 명시적으로 중단되지 않고 처리 완료 콜백이 나중에 이미 해제된 DMA 메모리 접근. AI 기반 코드 리뷰에서 발견된 결함.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53300) — CVE-2026-53300 공개 (CVSS 7.8)
