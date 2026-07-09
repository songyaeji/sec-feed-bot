---
slug: dolibarr-install-rce
first_seen: 2024-04-03
tags: [RCE, ERP, 설치프로세스, 입력검증]
cves: [CVE-2024-29477]
---

# Dolibarr ERP CRM 설치 프로세스 원격코드실행

오픈소스 ERP/CRM 플랫폼 Dolibarr v19.0.0 이하에서 발견된 설치 과정 취약점. 설치 중 사용자 입력에 대한 검증 부재로 인접 네트워크 공격자가 임의 코드 실행 가능(CVSS 8.8).

## 타임라인

- 2024-04-03 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-29477) — CVE-2024-29477: Dolibarr v19.0.0 설치 프로세스 입력 검증 누락 RCE
