---
slug: hyperv-type-confusion-rce
first_seen: 2026-06-09
tags: [RCE, Windows, Hyper-V, Virtualization]
cves: [CVE-2026-45641]
---

# Windows Hyper-V 타입 혼동 원격 코드 실행

Windows Hyper-V 가상머신 기능의 타입 혼동 결함으로 인해 인가된 공격자가 로컬에서 임의 코드를 실행할 수 있다. CVSS 8.4 높음 심각도로 평가됐다. Hyper-V는 기업 데이터센터 가상화의 핵심 플랫폼이므로, 로컬 특권 사용자가 호스트 커널 코드 실행을 획득하면 전체 가상 인프라가 위협받는다.

## 타임라인

- 2026-06-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-45641) — CVE-2026-45641 공시, CVSS 8.4 로컬 RCE

## 관련

- [[upnp-type-confusion-rce]] (동일 월의 Windows 타입 혼동 RCE)
- [[rdc-use-after-free-rce]] (Windows 클라이언트 RCE)
