---
slug: google-adk-ai-prompt-injection
first_seen: 2026-08-04
tags: [AI에이전트, 프롬프트인젝션, 보안테스트]
cves: []
---

**Google Agent Development Kit(ADK)** Python 저장소의 3개 AI 에이전트 워크플로우가 공개 GitHub 이슈를 통한 프롬프트 인젝션 공격에 노출되었다. Pillar Security는 **triage 에이전트**가 악의적 이슈로 조작되어 권한 있는 **code-fixing 에이전트**를 트리거하고 /adk-issue-fix 명령을 실행하는 공격 체인을 입증했다. Google은 해당 워크플로우를 삭제해 대응했다.

## 타임라인

- 2026-08-04 [The Hacker News](https://thehackernews.com/2026/08/google-deletes-3-adk-ai-workflows-after.html) — Google ADK AI 에이전트 프롬프트 인젝션 취약점 공개, 워크플로우 삭제 조치

## 관련
