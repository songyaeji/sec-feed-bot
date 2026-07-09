---
slug: rdc-use-after-free-rce
first_seen: 2026-06-09
tags: [RCE, Windows, Remote Desktop, Network]
cves: [CVE-2026-47653]
---

# Windows Remote Desktop Client 사용 후 해제 원격 코드 실행

Windows Remote Desktop Client(원격 데스크톱 클라이언트)의 메모리 관리 결함(사용 후 해제)으로 인해 미인증 공격자가 네트워크 경로로 임의 코드를 실행할 수 있다. CVSS 8.8 높음 심각도로 이번 배치에서 가장 높은 위협도를 가진 취약점이다. RDP는 관리자와 개발자의 원격 접근에 광범위하게 사용되므로, 이 RCE는 직접적인 초기 침해 경로가 될 수 있다.

## 타임라인

- 2026-06-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-47653) — CVE-2026-47653 공시, CVSS 8.8 네트워크 RCE

## 관련

- [[upnp-type-confusion-rce]] (동일 월의 Windows 네트워크 RCE)
- [[hyperv-type-confusion-rce]] (동일 월의 Windows 타입 혼동 RCE)
