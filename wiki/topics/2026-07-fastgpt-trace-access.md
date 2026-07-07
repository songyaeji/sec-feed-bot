---
slug: fastgpt-trace-access
first_seen: 2026-07-07
tags: [AI platform, access control, information disclosure]
cves: [CVE-2026-54602, CVE-2026-55418]
---

**FastGPT** 오픈소스 AI 지식 베이스 플랫폼의 다중 접근 제어 우회 취약점. GET /api/core/ai/record/getRecord가 인증은 수행하지만 팀 범위 검증이 없어 인증된 사용자가 다른 팀의 **LLM 요청·응답 로그**, **검색된 RAG 청크**, **프롬프트**에 무단 접근 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54602) — CVE-2026-54602 공개 (LLM 요청/응답 로그 접근)
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-55418) — CVE-2026-55418 공개 (CVSS 8.6, S3 객체 키 검증 부재 RCE)
