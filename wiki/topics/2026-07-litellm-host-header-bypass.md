---
slug: litellm-host-header-bypass
first_seen: 2026-07-08
tags: [AI, LLM, 인증우회]
cves: [CVE-2026-49468]
---

**LiteLLM** AI 게이트웨이의 HTTP 호스트 헤더 파싱 결함으로 특정 조건에서 미인증 공격자가 보안된 관리 경로에 접근 가능했던 취약점. 인증 검증 로직이 요청 경로를 잘못 해석하는 문제로, 1.84.0 이상에서 수정됐다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-49468) — CVE-2026-49468 공개 (CVSS 9.8)
