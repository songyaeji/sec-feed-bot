---
slug: llm-api-reasoning-trace-exposure
first_seen: 2026-08-12
tags: [AI, LLM, 정보유출, API보안]
cves: []
---

OpenAI, Anthropic, Google의 주요 LLM API에서 암호화된 내부 추론 과정(reasoning trace)을 복원할 수 있는 보안 허점이 발견됐다. 공개된 AI 에이전트 작업 로그에서 API 키와 비밀번호 등 실제 민감정보까지 노출됐으며, 암호화 기술 자체가 뚫린 것은 아니지만 암호화된 데이터가 세션·사용자·모델 간 재사용되는 설계상 결함이 원인이다.

## 타임라인

- 2026-08-12 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208029) — **OpenAI** GPT, **Anthropic** Claude, **Google** Gemini API 암호화 추론 과정 복원 가능, 세션·사용자 간 재사용

## 관련
