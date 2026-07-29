---
slug: broadcom-vmware-esxi-vm-escape
first_seen: 2026-07-29
tags: [VMware, 가상화, RCE, ESXi]
cves:
  - CVE-2026-47876
---

Broadcom이 VMware ESXi의 가상머신 탈출(VM escape) 취약점을 포함한 5개 취약점을 패치했다. 가장 심각한 취약점(CVE-2026-47876, CVSS 9.3)은 침해된 가상머신에서 호스트 상의 코드 실행을 가능하게 한다. ESXi, vCenter, Workstation, Fusion이 영향받는다.

## 타임라인

- 2026-07-29 [Security Affairs](https://securityaffairs.com/196231/security/broadcom-patches-critical-vmware-esxi-vulnerability-enabling-host-code-execution.html) — Broadcom VMware ESXi VM escape 취약점 패치, CVE-2026-47876 (CVSS 9.3)
- 2026-07-29 [The Hacker News](https://thehackernews.com/2026/07/three-critical-vmware-flaws-allow-auth.html) — 3가지 중대 VMware 취약점 공개: CVE-2026-59309 (CVSS 9.8, vCenter 인증우회) 외 코드 실행·VM escape 취약점

## 관련

[[vmware-avi-auth-bypass]] — VMware 인증 우회 취약점
