---
slug: vllm-trust-remote-code
first_seen: 2026-07-08
tags: [AI, LLM, 공급망]
cves: [CVE-2026-27893]
---

LLM 추론 엔진 **vLLM** 0.18.0 이전 버전의 모델 구현 파일이 사용자의 명시적 --trust-remote-code=False 설정을 무시한다. 서브 컴포넌트 로드 시 hardcoding으로 **trust_remote_code=True**를 강제해 악의적 모델 로드로 임의 코드 실행이 가능하다(CVSS 8.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-27893) — CVE-2026-27893 공개

## 관련
