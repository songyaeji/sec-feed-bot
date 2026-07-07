---
slug: localai-ssrf
first_seen: 2026-07-07
tags: [AI model server, SSRF, unauthenticated]
cves: [CVE-2026-59707]
---

LocalAI LLM 추론 서버의 서버 요청 위조(SSRF) 취약점. POST /models/apply 엔드포인트가 갤러리 URL을 검증 없이 처리하며 미인증 접근 허용. 공격자가 임의 내부 URL 요청으로 내부 서비스 정보 탈취 및 네트워크 스캔 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59707) — CVE-2026-59707 공개 (CVSS 8.6)
