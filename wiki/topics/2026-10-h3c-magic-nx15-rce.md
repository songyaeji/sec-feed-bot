---
slug: h3c-magic-nx15-rce
first_seen: 2026-10-19
tags: [원격코드실행, 네트워크기기, 공개익스플로잇]
cves: [CVE-2026-112370, CVE-2026-112371]
---

**H3C Magic NX15** 네트워크 기기의 두 가지 원격코드실행 취약점이 공개되었다. OS 명령 주입과 코드 주입 공격이 가능하며 두 취약점 모두 CVSS 9.9 심각도이고 공개 익스플로잇이 존재한다. 영향받는 버전은 NX15V100R017.

## 타임라인

- 2026-10-19 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-112370) — CVE-2026-112370 발표, /usr/bin/usrlist 함수 OS 명령 주입 (CVSS 9.9)
- 2026-10-19 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-112371) — CVE-2026-112371 발표, /api/esps RPC Interface 코드 주입 (CVSS 9.9)

## 관련

[[network-device-vulnerabilities]]
