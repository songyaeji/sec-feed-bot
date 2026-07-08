---
slug: libxfont2-buffer-overflow
first_seen: 2026-07-08
tags: [vulnerability, buffer-overflow, font-rendering]
cves: [CVE-2026-56001, CVE-2026-56002, CVE-2026-56003]
---

libXfont2 폰트 렌더링 라이브러리의 다중 글리프 처리 결함으로 인한 힙 버퍼 오버플로우 취약점들 (CVSS 8.5). BitmapScaleBitmaps, pcfReadFont, ComputeScaledProperties 함수의 경계 검증 누락으로 X 클라이언트 권한이 있는 공격자가 X 서버 내에서 코드 실행 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-56001) — CVE-2026-56001 공개 (BitmapScaleBitmaps 오버플로우)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-56002) — CVE-2026-56002 공개 (pcfReadFont 오버플로우)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-56003) — CVE-2026-56003 공개 (ComputeScaledProperties 오버플로우)

## 관련

[[xorg-xwayland-pcx-overflow]]

