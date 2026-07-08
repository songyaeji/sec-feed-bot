---
slug: freerdp-bitmap-overflow
first_seen: 2026-07-08
tags: [RDP, 클라이언트, 원격접근]
cves: [CVE-2026-40033, CVE-2026-44420, CVE-2026-44421, CVE-2026-45700]
---

원격 데스크톱 프로토콜(RDP) 오픈소스 구현 **FreeRDP** 3.26.0 이전 버전의 평면 비트맵 디코더에서 RLE 데이터 처리 시 X 좌표를 부정확하게 검증해 힙 오버플로우가 발생한다(CVSS 9.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-40033) — CVE-2026-40033: gdi_CacheToSurface 힙 오버플로우 (CVSS 8.8)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44420) — CVE-2026-44420: 클립보드 채널 힙 오버플로우 (CVSS 8.8)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44421) — CVE-2026-44421: RDPGFX 힙 오버플로우 (CVSS 8.8)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-45700) — CVE-2026-45700 공개

## 관련
