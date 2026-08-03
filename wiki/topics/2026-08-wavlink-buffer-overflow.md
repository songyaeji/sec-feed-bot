---
slug: wavlink-buffer-overflow
first_seen: 2026-08-03
tags: [버퍼오버플로우, NAS, 산업기기, 원격코드실행, RCE]
cves: [CVE-2026-18588, CVE-2026-18589]
---

# Wavlink WL-NU516U1 NAS 버퍼오버플로우 취약점

Wavlink **WL-NU516U1** NAS 기기의 nas.cgi 파일에서 2개의 스택 기반 버퍼오버플로우 취약점이 발견되었다. 둘 다 CVSS 9.8의 심각한 취약점으로, 원격 공격자가 인증 없이 악용 가능하며, 공개 exploit이 존재한다. 벤더가 신속하게 대응해 패치를 배포했다.

## 타임라인

- 2026-08-03 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-18588) — CVE-2026-18588 nas.cgi fgets 버퍼오버플로우 공개 (CVSS 9.8)
- 2026-08-03 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-18589) — CVE-2026-18589 nas.cgi change_password 버퍼오버플로우 공개 (CVSS 9.8, 공개 exploit 존재)

## 관련

없음
