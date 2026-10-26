---
slug: praisonai-code-execution
first_seen: 2026-07-11
tags: [AI보안, LLM공격, RCE, 코드생성]
cves: [CVE-2026-61447]
---

**PraisonAI**의 CodeAgent 컴포넌트가 LLM이 생성한 Python 코드를 AST 검증·import 제한·샌드박스 없이 직접 실행해 환경 변수 탈취와 호스트 임의 코드 실행이 가능하다. 프롬프트 주입으로 공격자가 LLM 출력을 조종할 수 있어 신뢰성 있는 방어 불가능.

## 타임라인

- 2026-07-11 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-61447) — CVE-2026-61447 공개, CVSS 10.0, LLM 생성 코드 직접 실행 취약점
