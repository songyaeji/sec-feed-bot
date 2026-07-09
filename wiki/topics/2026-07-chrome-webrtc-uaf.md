---
slug: chrome-webrtc-uaf
first_seen: 2026-07-08
tags: [Chrome, WebRTC, RCE, 메모리손상]
cves: [CVE-2026-15121]
---

**Google Chrome** 150.0.7871.115 이전 버전의 WebRTC 구현에서 사용 후 해제(UAF) 메모리 손상 취약점 발견. 악의적 HTML 페이지로 트리거 가능하며 샌드박스 내 임의 코드 실행 가능. Chrome 자동 업데이트로 빠르게 배포됨.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15121) — CVE-2026-15121 (CVSS 8.8) WebRTC 사용 후 해제 RCE
