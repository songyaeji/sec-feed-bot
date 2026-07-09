---
slug: ultravnc-buffer-overflow
first_seen: 2026-07-01
tags: [RCE, VNC, 버퍼오버플로우, 무인증]
cves: [CVE-2026-7840]
---

# UltraVNC 원격데스크톱 전역 버퍼 오버플로우 원격코드실행

원격데스크톱 솔루션 UltraVNC repeater v1.8.2.2 이하에서 발견된 중대 취약점. 임베디드 HTTP 관리 서버의 **wi_senderr**, **wi_replyhdr** 함수에서 전역 버퍼 **hdrbuf**(1000바이트)에 검증 없이 사용자 요청 URI를 기록(unchecked sprintf)하여 인증 없는 원격 코드 실행 가능(CVSS 9.8).

## 타임라인

- 2026-07-01 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-7840) — CVE-2026-7840: UltraVNC repeater v1.8.2.2 웹 관리 서버 전역 버퍼 오버플로우
