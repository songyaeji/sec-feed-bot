---
slug: shibby-tomato-buffer-overflow
first_seen: 2026-07-18
tags: [라우터펌웨어, 범위외접근, 원격공격]
cves: [CVE-2026-16095, CVE-2026-16096, CVE-2026-16097]
---

Shibby Tomato 1.28 RT-N5x MIPSR2 Build 124에서 3개의 버퍼 오버플로우 및 범위 외 접근 취약점 발견. 인자 조작으로 범위 외 메모리 쓰기 가능하며 원격 공격 가능. 해당 프로젝트는 FreshTomato로 대체됨.

## 타임라인

- 2026-07-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16095) — CVE-2026-16095 (OOB write) 공개
- 2026-07-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16096) — CVE-2026-16096 (버퍼 오버플로우) 공개
- 2026-07-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16097) — CVE-2026-16097 (버퍼 오버플로우) 공개

## 관련

[[router-firmware-vulnerabilities]]
