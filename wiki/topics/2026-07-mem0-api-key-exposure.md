---
slug: mem0-api-key-exposure
first_seen: 2026-07-07
tags: [AI memory platform, API key exposure, SSRF, unauthenticated]
cves: [CVE-2026-59706]
---

mem0 AI 메모리 플랫폼의 API 키 평문 노출 취약점. 설정 API 엔드포인트(/api/v1/config/)가 미인증 상태로 노출되어 OpenAI, Claude 등의 **LLM API 키**를 평문으로 조회 가능. ollama_base_url 매개변수 조작으로 SSRF 공격도 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59706) — CVE-2026-59706 공개 (CVSS 9.3)
