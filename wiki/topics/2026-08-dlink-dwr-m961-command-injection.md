---
slug: dlink-dwr-m961-command-injection
first_seen: 2026-08-08
tags: [명령주입, 라우터보안, 원격코드실행]
cves: [CVE-2026-71944, CVE-2026-71945, CVE-2026-71946, CVE-2026-71947, CVE-2026-71948, CVE-2026-71949, CVE-2026-71950, CVE-2026-71951]
---

D-Link **DWR-M961** C1 하드웨어, 펌웨어 v1.1.5_C1_202607071108 이전 버전의 
여러 HTTP 관리 인터페이스에 OS 명령 주입 취약점이 발견됐다. fota_url, host, ussdValue, 
selectMenuValue, action_value, IMEI_value 등 사용자 입력이 필터링 없이 
명령줄에 전달되어 **루트 권한 코드 실행**을 허용한다. 
8개의 관련 CVE(CVE-2026-71944~71951)가 동시 공개됐으며 CVSS는 모두 9.8.

## 타임라인

- 2026-08-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71944) — /boafrm/formLtefotaUpgradeQuectel 명령 주입 CVE-2026-71944 공개
- 2026-08-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71945) — /boafrm/formLtefotaUpgradeFibocom 명령 주입 CVE-2026-71945 공개
- 2026-08-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71946) — /boafrm/formPingDiagnosticRun 명령 주입 CVE-2026-71946 공개
- 2026-08-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71947) — /boafrm/formTracerouteDiagnosticRun 명령 주입 CVE-2026-71947 공개
- 2026-08-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71948) — /boafrm/formDebugDiagnosticRun 명령 주입 CVE-2026-71948 공개
- 2026-08-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71949) — /boafrm/formUSSDSetup 명령 주입 CVE-2026-71949 공개
- 2026-08-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71950) — /boafrm/formSmsManage 명령 주입 CVE-2026-71950 공개
- 2026-08-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71951) — /boafrm/formIMEISetup 명령 주입 CVE-2026-71951 공개

## 관련

[[zbtlink-router-backdoor]]
