---
slug: multitenant-privilege-bypass
first_seen: 2026-07-27
tags: [SaaS, 멀티테넌트, 권한우회, 액세스통제]
cves: [CVE-2026-15630]
---

SaaS 멀티테넌트 환경에서 비전역 조직 관리자가 URL 쿼리 파라미터(?id=)와 요청 본문 간의 불일치를 악용해 테넌트 경계를 우회할 수 있는 취약점. 다른 테넌트의 리소스 삭제, 생성, 수정이 가능하다. CVSS 9.9로 평가됨.

## 타임라인

- 2026-07-23 — 취약점 발견
- 2026-07-27 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15630) — CVE-2026-15630 공개
