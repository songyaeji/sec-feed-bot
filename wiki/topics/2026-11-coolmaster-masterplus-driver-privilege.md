---
slug: coolmaster-masterplus-driver-privilege
first_seen: 2026-11-14
tags: [CoolerMaster, 커널드라이버, 권한상향, 로컬공격]
cves: [CVE-2026-129255]
---

# CoolerMaster MASTERPLUS+ — 커널 드라이버 권한 상향

**CoolerMaster** MASTERPLUS+ 1.9.6 시스템 모니터링 소프트웨어의 WinRing0x64.sys 커널 드라이버에서 sub_11504 함수의 PhysicalAddress 인자 조작으로 기본 권한 설정 오류(CVSS 8.8). 로컬 공격자가 SYSTEM 권한으로 상향 가능. 공개 익스플로잇 있으며 벤더 미응답.

## 타임라인

- 2026-11-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-129255) — CVE-2026-129255 드라이버 권한 설정 오류 CVSS 8.8
