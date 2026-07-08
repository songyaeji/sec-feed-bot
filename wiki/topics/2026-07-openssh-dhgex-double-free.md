---
slug: openssh-dhgex-double-free
first_seen: 2026-07-08
tags: [OpenSSH, 메모리안전, 더블프리]
cves: [CVE-2026-55653]
---

OpenSSH의 **DH-GEX**(Diffie-Hellman Group Exchange) 클라이언트 경로에서 FIPS 모드 검증 중 메모리 **더블 프리** 버그. 악의적 SSH 서버가 공격자 제어 DH-GEX 그룹으로 클라이언트를 표적하면 크래시 또는 권한상향 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-55653) — CVE-2026-55653: DH-GEX 더블 프리 (CVSS 4.3)

## 관련
