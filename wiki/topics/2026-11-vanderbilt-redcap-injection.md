---
slug: vanderbilt-redcap-injection
first_seen: 2026-11-18
tags: [research-platform, code-injection, rce]
cves: [CVE-2026-90817]
---

Vanderbilt 대학의 Research Electronic Data Capture(REDCap) 플랫폼에 코드 인젝션 취약점. 미인증 공격자가 조작된 HTTP 요청을 통해 서버에서 임의 코드를 실행할 수 있다. 연구기관과 의료 조직에서 광범위하게 채용되어 있어 이차 피해 우려.

## 타임라인

- 2026-11-18 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-90817) — CVE-2026-90817 공개, 미인증 코드 인젝션 RCE
- 2026-11-19 [The Hacker News](https://thehackernews.com/2026/11/cisa-warns-of-4-exploited-flaws-linked.html) — CISA Known Exploited Vulnerabilities(KEV) 목록에 공식 추가, 실제 악용 중 확인
