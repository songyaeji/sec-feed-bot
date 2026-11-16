---
slug: sglang-deserialization-rce
first_seen: 2026-09-11
tags: [역직렬화취약점, LLM플랫폼, 무인증RCE]
cves: [CVE-2026-86793]
---

# SGLang — 무인증 역직렬화 원격코드실행

LLM 플랫폼 **SGLang**의 `/update_weights_from_tensor` 엔드포인트에서 **pickle 역직렬화** 취약점이 발견됐다. 비활성화된 인증 설정 시 SafeUnpickler 정책이 builtins.import와 builtins.getattr을 허용해 pickle REDUCE 공격으로 코드 실행이 가능하다.

## 타임라인

- 2026-09-11 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-86793) — CVE-2026-86793 CVSS 9.8 공개, SGLang 무인증 pickle 역직렬화 취약점 확인

## 관련
