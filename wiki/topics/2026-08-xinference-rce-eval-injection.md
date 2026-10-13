---
slug: xinference-rce-eval-injection
first_seen: 2026-08-21
tags: [AI, RCE, eval주입, LLM]
cves: [CVE-2026-61539]
---

오픈소스 **Xinference** 2.5.0 이하에서 공격자의 프롬프트가 eval() 인자로 직접 전달되는 eval() 주입 취약점으로 미인증 공격자가 서버 프로세스 권한으로 명령 실행 가능 (CVSS 10.0). **LLM** 추론 인프라 표적의 심각한 위협. 버전 2.7.0에서 수정됨.

## 타임라인

- 2026-08-21 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-61539) — CVE-2026-61539 Xinference eval() 주입 원격코드실행 CVSS 10.0 공개

## 관련
