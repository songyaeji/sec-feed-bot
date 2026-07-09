---
slug: totolink-cp900l-hardcoded-password
first_seen: 2024-05-24
tags: [RCE, 라우터, 하드코드]
cves: [CVE-2024-35395, CVE-2024-35397, CVE-2024-35399]
---

# TOTOLINK CP900L 라우터 다중 임의코드실행 취약점

TOTOLINK CP900L v4.1.5 라우터에서 발견된 세 가지 원격코드실행 취약점. 하드코드 비밀번호, NTP 동기화 명령 인젝션, 로그인 함수 스택 오버플로우로 인증 없는 root 접근 및 원격 명령 실행 가능.

## 타임라인

- 2024-05-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-35395) — CVE-2024-35395 (CVSS 8.8): /etc/shadow.sample 하드코드 비밀번호로 root 로그인
- 2024-05-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-35397) — CVE-2024-35397 (CVSS 8.8): NTPSyncWithHost 함수 hostTime 파라미터 명령 인젝션
- 2024-05-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-35399) — CVE-2024-35399 (CVSS 8.8): loginAuth 함수 password 파라미터 스택 오버플로우
