---
slug: arc-sensors-cli-privesc
first_seen: 2026-07-09
tags: [권한상향, 동기화, CLI명령, 장치설정]
cves: [CVE-2026-33390]
---

# Arc Sensors 동기화 기능 권한 할당 오류

**Arc sensors** 동기화 기능에서 센서가 CLI(command-line interface) 권한을 부정확하게 받음. 제한된 권한만 가진 인증 사용자가 동기화를 통해 관리자 권한의 CLI 명령을 실행하여 기기 설정을 변경하거나 시스템 영향 야기 가능(CVSS 8.1).

## 타임라인

- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-33390) — CVE-2026-33390: Arc sensors 동기화 권한 할당 오류
