---
slug: draytek-vigor2960-rce-eol
first_seen: 2026-10-20
tags: [원격코드실행, 라우터, 지원중단기기]
cves: [CVE-2026-113389, CVE-2026-113390, CVE-2026-113391]
---

**DrayTek Vigor2960** 라우터의 웹 관리 인터페이스 CGI 프로세스에서 명령 주입 취약점 3건이 발견되었다. 모두 CVSS 9.9 심각도이며 공개 익스플로잇이 존재한다. 1.5.1.7 버전에서 수정되었으나 해당 제품은 제한 지원(EoS) 상태로 보안 패치 제공이 중단되었다.

## 타임라인

- 2026-10-20 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-113389) — CVE-2026-113389 발표, /cgi-bin/mainfunction.cgi set_table 명령 주입 (CVSS 9.9)
- 2026-10-20 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-113390) — CVE-2026-113390 발표, /cgi-bin/mainfunction.cgi sub_182B0 OS 명령 주입 (CVSS 9.9)
- 2026-10-20 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-113391) — CVE-2026-113391 발표, /cgi-bin/mainfunction.cgi uploadlangs 파일 업로드 명령 주입 (CVSS 9.9)

## 관련

[[network-device-eol-vulnerabilities]]
[[router-security]]
