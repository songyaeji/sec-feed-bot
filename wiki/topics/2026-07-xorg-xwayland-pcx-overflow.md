---
slug: xorg-xwayland-pcx-overflow
first_seen: 2026-07-08
tags: [vulnerability, buffer-overflow, x11, xwayland]
cves: [CVE-2026-55999]
---

X 서버 및 Xwayland의 PCX 폰트 처리 결함으로 인한 힙 버퍼 오버플로우 취약점 **CVE-2026-55999** (CVSS 8.5). X 클라이언트 연결 권한이 있는 공격자가 SetFont 명령으로 글리프 경계 검증 실패를 통해 힙 오버플로우를 유발하여 X 서버 내에서 코드 실행 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-55999) — CVE 공개

## 관련

