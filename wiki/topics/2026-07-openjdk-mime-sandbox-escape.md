---
slug: openjdk-mime-sandbox-escape
first_seen: 2026-07-08
tags: [샌드박스탈출, 우분투]
cves: [CVE-2026-10037]
---

Ubuntu의 OpenJDK 패키지에 포함된 .jar MIME 핸들러가 mailcap 설치 시 실행 권한으로 표시되어, xdg-desktop-portal을 통해 접근하는 sandboxed 애플리케이션이 시스템 명령을 실행할 수 있게 된다. Ubuntu 기본 환경의 샌드박스 격리가 우회된다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-10037) — CVE-2026-10037 (CVSS 8.8) 공개

## 관련

