---
slug: cf-manager-ssrf-rce
first_seen: 2026-11-18
tags: [ssrf, rce, cloudflare]
cves: [CVE-2026-71499]
---

cf-manager 1.1.2 이전의 미검증 URL 페치 취약점. 배포 API 접근 또는 미인증 접근 시 공격자가 내부 리소스 접근 또는 공격자 제어 JavaScript 실행으로 Cloudflare Workers 계정 침해 가능.

## 타임라인

- 2026-11-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71499) — CVE-2026-71499 CVSS 10.0 공개, 1.1.2에서 수정
