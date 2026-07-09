---
slug: dolibarr-upload-rce
first_seen: 2024-06-18
tags: [RCE, ERP, 파일업로드]
cves: [CVE-2024-37821]
---

# Dolibarr ERP CRM 템플릿 업로드 원격코드실행

오픈소스 ERP/CRM 플랫폼 Dolibarr v19.0.1 이하에서 발견된 파일 업로드 취약점. Upload Template 기능에서 **.SQL** 파일 업로드를 통한 임의 코드 실행 가능(CVSS 8.8).

## 타임라인

- 2024-06-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-37821) — CVE-2024-37821: Dolibarr v19.0.1 .SQL 파일 업로드 RCE
