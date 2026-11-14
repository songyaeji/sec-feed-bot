---
slug: edimax-br6478-buffer-overflow
first_seen: 2026-11-14
tags: [Edimax, 라우터, 버퍼오버플로우, 공개익스플로잇]
cves: [CVE-2026-129250]
---

# Edimax BR6478ACV2 — 버퍼오버플로우 원격코드실행

**Edimax** BR6478ACV2 1.23 펌웨어의 웹 인터페이스 formPPTPSetup 함수에서 pptpUserName 인자의 입력 검증 부족으로 인한 스택 버퍼 오버플로우(CVSS 9.9). 미인증 원격 코드 실행 가능. 공개 익스플로잇 있으며 벤더 미응답.

## 타임라인

- 2026-11-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-129250) — CVE-2026-129250 formPPTPSetup pptpUserName 버퍼오버플로우 CVSS 9.9
