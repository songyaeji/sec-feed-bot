---
slug: edimax-buffer-overflow
first_seen: 2026-08-16
tags: [Edimax, 라우터, 버퍼오버플로우, 무패치]
cves: [CVE-2026-19959, CVE-2026-19961]
---

# Edimax EW-7478APC — 다중 버퍼 오버플로우

**Edimax EW-7478APC 1.04** 무선 공유기에서 두 CGI 함수의 입력 검증 부족으로 인한 다중 스택 버퍼 오버플로우(CVSS 9.9). 공개 익스플로잇이 있으며 벤더 미응답.

## 타임라인

- 2026-08-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-19959) — CVE-2026-19959 formWanTcpipSetup 함수 pppUserName 검증 누락
- 2026-08-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-19961) — CVE-2026-19961 formWlSiteSurvey 함수 selSSID 검증 누락
