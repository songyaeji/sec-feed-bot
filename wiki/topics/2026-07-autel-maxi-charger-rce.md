---
slug: autel-maxi-charger-rce
first_seen: 2026-07-21
tags: [IoT, 충전기, RCE, 미인증]
cves: [CVE-2026-8984]
---

Autel Maxi Charger Single 펌웨어 V1.03.51 이하가 TCP 포트 9002의 서비스에서 미인증 원격코드실행을 허용한다. /test 엔드포인트로 조작된 요청을 전송하면 기기가 공격자 제어 파일을 다운로드, 추출, 루트 권한으로 실행한다.

## 타임라인

- 2026-07-21 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-8984) — CVE-2026-8984 CVSS 9.8 공개, 미인증 RCE 취약점 확인
