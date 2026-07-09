---
slug: upnp-type-confusion-rce
first_seen: 2026-06-09
tags: [RCE, Windows, UPnP, Network]
cves: [CVE-2026-45635]
---

# Windows UPnP 타입 혼동 원격 코드 실행

Windows 범용 플러그 앤 플레이(UPnP) 드라이버의 타입 혼동 결함으로 인해 미인증 공격자가 네트워크 경로로 임의 코드를 실행할 수 있다. CVSS 8.1 높음 심각도로 평가됐다. UPnP는 스마트홈 기기, 보안 카메라, 네트워크 장치 간 자동 인식·통신에 광범위하게 사용되므로 공격 표면이 크다.

## 타임라인

- 2026-06-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-45635) — CVE-2026-45635 공시, CVSS 8.1 RCE

## 관련

- [[hyperv-type-confusion-rce]] (동일 월의 Windows 타입 혼동 RCE)
- [[rdc-use-after-free-rce]] (Windows 클라이언트 RCE)
