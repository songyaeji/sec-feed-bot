---
slug: lantronix-serial-auth-bypass
first_seen: 2026-09-22
tags: [serial-server, industrial-control, auth-bypass, supply-chain]
cves: [CVE-2026-80155]
---

Lantronix SLC8000, SLC9000, EMG8500/7500 및 모든 firmware 버전의 SLB882/SLCx 직렬 서버의 웹관리 포털에서 snprintf 버퍼 오버플로우로 인한 경로 조작. 세션 쿠키 파일 경로 truncate를 통해 인증 검증을 임의 파일로 우회할 수 있으며, 이를 통해 설정 파일 읽기와 임의 파일 업로드로 완전한 원격코드실행 달성 가능. 직렬 연결된 하위 기기까지 광범위 영향 (CVSS 10.0).

## 타임라인

- 2026-09-22 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-80155) — CVE-2026-80155 공개, 웹관리 포털 미인증 auth bypass 및 RCE
