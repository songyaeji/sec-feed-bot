---
slug: litellm-guardrails-sandbox
first_seen: 2026-07-08
tags: [AI, LLM, 샌드박싱]
cves: [CVE-2026-59821]
---

**LiteLLM** 1.82.0-stable 이전 버전의 Custom Code Guardrails 프로덕션 생성/수정 경로가 테스트 엔드포인트와 다른 보안 검증을 사용하지 않아, 권한을 가진 사용자가 샌드박싱 규칙을 우회하는 악의적 코드를 프로덕션에 배포할 수 있는 취약점.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59821) — CVE-2026-59821 공개 (CVSS N/A)
