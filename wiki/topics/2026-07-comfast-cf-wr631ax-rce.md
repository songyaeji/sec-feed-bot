---
slug: comfast-cf-wr631ax-rce
first_seen: 2026-07-12
tags: [명령인젝션, 무선공유기, RCE]
cves: [CVE-2026-15511]
---

# Comfast CF-WR631AX V3 원격 명령 실행

Comfast 무선 공유기의 FastCGI 백엔드에서 filename 인자 조작을 통한 명령 인젝션 취약점. CVSS 9.8 중대도. 벤더가 미응답하고 공개 익스플로잇이 있다.

## 타임라인

- 2026-07-12 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15511) — CVE-2026-15511 공개. CF-WR631AX V3 up to 2.7.0.8 취약. system_wl_upload_pic_file 함수의 /usr/bin/webmgnt에서 파일명 인자 검증 누락으로 OS 명령 삽입 가능. 원격 공격 가능하며 공개 익스플로잇 있음.
