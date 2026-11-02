---
slug: dlink-router-tftp-vulnerabilities
first_seen: 2026-11-02
tags: [라우터보안, TFTP취약점, 제로데이]
cves: [CVE-2026-120189]
---

D-Link DIR-505 라우터의 TFTP 파일 업로드 핸들러에서 스택 버퍼오버플로우 취약점이 발견됐다. CVSS 10.0으로 평가되며 미인증 원격 공격으로 완전한 기기 제어와 펌웨어 변조가 가능하다. 공개 익스플로잇이 존재한다.

## 타임라인

- 2026-11-02 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-120189) — CVE-2026-120189 DIR-505 1.10B02 TFTP 업로드 strcpy 버퍼오버플로우 공개 (CVSS 10.0)

## 관련

[[wavlink-iot-vulnerabilities]]
