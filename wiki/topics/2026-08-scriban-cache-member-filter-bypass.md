---
slug: scriban-cache-member-filter-bypass
first_seen: 2026-08-16
tags: [템플릿엔진, 권한상향, 캐싱버그]
cves: [CVE-2026-74790]
---

# Scriban — 캐시 정책 우회 접근 제어 탈취

**Scriban** 7.0.0 이전이 TypedObjectAccessor를 Type만으로 캐싱하여, 같은 객체의 MemberFilter 변경 시 이전 캐시를 재사용. TemplateContext를 재사용하는 환경에서 제한된 필드에 접근 가능하며, 다중 테넌트 환경에서는 한 테넌트의 필터링을 다른 테넌트가 우회 가능.

## 타임라인

- 2026-08-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-74790) — CVE-2026-74790 CVSS 9.1 공개, 캐싱으로 인한 샌드박스 우회 확인

## 관련

[[scriban-access-modifier-bypass]] — Scriban 접근 제한자 우회 취약점
