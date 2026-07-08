---
slug: bentoml-openllm-rce
first_seen: 2026-07-08
tags: [LLM, 커맨드인젝션, 로컬]
cves: [CVE-2026-15035]
---

**bentoml OpenLLM** 0.6.30 Model Repository Directory Name 핸들러의 `async_run_command` 함수에서 `cmd` 인수 검증 부재. 로컬 공격자가 **커맨드 인젝션**으로 시스템 명령 실행 가능하며, 공급망 공격 벡터로 악용 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15035) — CVE-2026-15035: 로컬 커맨드 인젝션 (CVSS 5.3)

## 관련
