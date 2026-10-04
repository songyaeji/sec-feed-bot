---
slug: berriai-litellm-security-vulnerabilities
first_seen: 2026-06-05
tags: [AI, LLM]
cves: [CVE-2026-42271, CVE-2026-42208]
---

BerriAI LiteLLM은 다양한 LLM API 통합 프록시 서비스다. 저권한 내부 사용자 인증으로도 임의 명령 실행과 데이터베이스 접근이 가능한 2개 취약점이 CISA KEV에 등재되어 실제 악용이 확인됐다.

## 타임라인

- 2026-06-08 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-42271) — CVE-2026-42271 명령 인젝션 취약점 CISA 등재, 저권한 내부 사용자 키로 호스트 임의 명령 실행
- 2026-05-08 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-42208) — CVE-2026-42208 SQL 인젝션 취약점, 프록시 데이터베이스 읽기·수정 및 자격증명 탈취 가능

## 관련

[[ai-security-threats]]
