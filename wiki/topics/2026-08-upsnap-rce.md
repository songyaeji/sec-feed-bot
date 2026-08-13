---
slug: upsnap-rce
first_seen: 2026-08-13
tags: [RCE, 미인증, IoT]
cves: [CVE-2026-49819]
---

UpSnap 4.4.1~5.3.5 버전의 pb.HandlerInitSuperuser 엔드포인트 (/api/upsnap/init-superuser)에 인증, 설정 토큰, IP 화이트리스트, 속도 제한이 없다. 신규 설치 시 totalSuperusers > 0 조건이 거짓이어서 미인증 공격자가 초기 슈퍼유저 계정을 등록한 후 장기 JWT를 받아 루트 원격코드실행으로 피벗할 수 있다 (exec.CommandContext에서 /bin/sh -c 실행).

## 타임라인

- 2026-08-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-49819) — CVE-2026-49819 CVSS 9.8 공개, 신규 설치 미인증 RCE 취약점 확인, 5.4.0에서 수정됨
