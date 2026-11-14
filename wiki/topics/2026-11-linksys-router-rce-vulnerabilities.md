---
slug: linksys-router-rce-vulnerabilities
first_seen: 2026-11-02
tags: [라우터보안, 가정용기기, 버퍼오버플로우, 인증우회]
cves: [CVE-2026-120283, CVE-2026-121615, CVE-2026-127275, CVE-2026-127277]
---

Linksys 공유기 제품군에서 다중 보안 취약점이 발견됐다. E8450의 웹 포털 스택 버퍼오버플로우와 E5600의 인증 우회 취약점 모두 CVSS 10.0으로 평가되며 미인증 원격 공격으로 완전한 기기 제어가 가능하다. 공개 익스플로잇이 존재한다.

## 타임라인

- 2026-11-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-127277) — CVE-2026-127277 EA8100 1.0.3.216940 SMB Service ANON_ACCESS 인자 변조 미인증 접근 (CVSS 10.0)
- 2026-11-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-127275) — CVE-2026-127275 EA8100 1.0.3.216940 JNAP API SetRemoteSetting 미인증 설정 변조 (CVSS 10.0)
- 2026-11-04 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-121615) — CVE-2026-121615 E5600 1.1.0.26 mesh_login.cgi 인증 우회 (CVSS 10.0, 단종 제품)
- 2026-11-02 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-120283) — CVE-2026-120283 E8450 1.2.00.360516 웹 포털 strcpy 버퍼오버플로우 공개 (CVSS 10.0)

## 관련

[[wavlink-iot-vulnerabilities]]
