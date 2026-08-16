---
slug: scriban-access-modifier-bypass
first_seen: 2026-08-16
tags: [템플릿엔진, 권한상향, 접근제어우회]
cves: [CVE-2026-73061]
---

# Scriban — 접근 제한자 우회 취약점

**Scriban** 템플릿 엔진 7.2.2 이전의 TypedObjectAccessor에서 접근 제한자 검증 실패로, 템플릿 코드가 private, internal, init-only setter를 갖는 CLR 객체 속성을 검증 없이 수정 가능. 개인키나 중요 설정값 같은 보호된 속성을 공격자가 변경 가능.

## 타임라인

- 2026-08-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-73061) — CVE-2026-73061 CVSS 9.8 공개, TypedObjectAccessor 우회 확인

## 관련

[[scriban-cache-member-filter-bypass]] — Scriban 캐시 정책 우회 접근 제어 탈취
