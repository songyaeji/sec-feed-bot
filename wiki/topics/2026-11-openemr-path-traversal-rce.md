---
slug: openemr-path-traversal-rce
first_seen: 2026-11-08
tags: [원격코드실행, 의료정보시스템, 경로조작, CVE-2026-124450]
cves: [CVE-2026-124450]
---

**OpenEMR** 의료정보시스템의 fax/sms 모듈 disposeDocument 동작에서 경로 조작과 접근 제어 결함으로 저권한 인증 사용자가 임의 파일을 읽고 쓸 수 있는 취약점이 발견되었다. sqlconf.php 파일 읽기로 데이터베이스 자격증명을 탈취하고 웹 공격 가능 폴더에 웹셸을 배치해 원격코드실행을 달성 가능하다.

## 타임라인

- 2026-11-08 [NVD CVE-2026-124450](https://nvd.nist.gov/vuln/detail/CVE-2026-124450) — OpenEMR 8.3.0 이전 경로 조작 및 접근 제어 취약점 CVSS 9.9
