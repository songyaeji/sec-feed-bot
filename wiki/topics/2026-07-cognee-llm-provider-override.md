---
slug: cognee-llm-provider-override
first_seen: 2026-07-07
tags: [AI security, improper access control, LLM]
cves: [CVE-2026-58473]
---

Cognee 플랫폼의 미인증 LLM 제공자 설정 덮어쓰기 취약점. settings 엔드포인트가 인증을 검증하지 않아 누구나 자가등록 후 전역 LLM 설정을 조작 가능. 모든 LLM 요청을 공격자 계정으로 리다이렉트해 API 키 탈취 및 프롬프트 조작 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-58473) — CVE-2026-58473 공개 (CVSS 9.1)
