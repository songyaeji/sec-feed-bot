---
slug: litellm-health-endpoint
first_seen: 2026-07-08
tags: [AI, LLM, 환경변수]
cves: [CVE-2026-59819]
---

**LiteLLM** 1.83.10-stable 이전 버전의 `/health/test_connection` 엔드포인트가 환경변수와 OIDC 파일 참조를 litellm_params에서 해석하여, 권한을 가진 호출자가 시스템 설정을 조작할 수 있는 취약점. 프록시 관리자가 민감 정보에 접근하거나 설정을 변경할 수 있다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59819) — CVE-2026-59819 공개 (CVSS N/A)
