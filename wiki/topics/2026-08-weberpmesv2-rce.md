---
slug: weberpmesv2-rce
first_seen: 2026-08-13
tags: [ERP, MES, RCE, 미인증]
cves: [CVE-2026-49827]
---

WebErpMesv2 1.19 이하 버전에서 자체 등록 가능한 사용자가 HR Expense scan_file 매개변수를 통해 임의 PHP 파일을 업로드하여 원격코드실행을 달성할 수 있다. 공개 등록(초대 불필요)과 깨진 역할 미들웨어(CheckUserRole이 RouteNotFoundException을 무시)를 결합하면 기본 설치에서 사실상 미인증 RCE가 가능하다.

## 타임라인

- 2026-08-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-49827) — CVE-2026-49827 CVSS 9.8 공개, 미인증 RCE 취약점 확인, 커밋 5c54862fa044b363fd2be03d586750e81afd6818에서 수정됨
