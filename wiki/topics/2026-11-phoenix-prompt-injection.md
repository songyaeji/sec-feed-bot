---
slug: phoenix-prompt-injection
first_seen: 2026-11-16
tags: [프롬프트인젝션, AI플랫폼, 자격증명탈취]
cves: [CVE-2026-53998]
---

# Phoenix — 프롬프트 인젝션 환경변수 탈취

AI 관측성 플랫폼 **Phoenix** 13.0.0~15.6.x의 applyChatTemplate GraphQL 쿼리에서 **프롬프트 인젝션** 취약점이 발견됐다. F-string 템플릿 처리 중 사용자 입력이 미검증되면서 환경변수, 세션 토큰, 암호화 키가 탈취 가능하다.

## 타임라인

- 2026-11-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53998) — CVE-2026-53998 CVSS 10.0 공개, GraphQL 프롬프트 인젝션 확인

## 관련
