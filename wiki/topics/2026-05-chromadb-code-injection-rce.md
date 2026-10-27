---
slug: chromadb-code-injection-rce
first_seen: 2026-05-18
tags: [ChromaDB, AI, LLM, CodeInjection, RCE]
cves: [CVE-2026-45829]
---

벡터 데이터베이스 ChromaDB v1.0.0 이상에서 미인증 엔드포인트 /api/v2/tenants/{tenant}/databases/{db}/collections에 악의적 모델 저장소와 trust_remote_code=true로 임의 코드 실행. LLM 애플리케이션 인프라 표적.

## 타임라인

- 2026-05-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-45829) — CVE-2026-45829 공개 (CVSS 10.0)
