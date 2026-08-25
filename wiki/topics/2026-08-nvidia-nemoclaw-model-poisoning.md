---
slug: nvidia-nemoclaw-model-poisoning
first_seen: 2026-08-25
tags: [LLM보안, AI모델공격, 로컬LLM위협, 모델중독]
cves: []
---

# NVIDIA NemoClaw — 웹페이지 LLM 모델 중독

Oasis Security가 **NVIDIA NemoClaw**에서 인증 없는 로컬 **Ollama** 인스턴스를 원격에서 제어할 수 있는 취약점을 공개했다. 공격자가 악의적 웹페이지로 AI 에이전트가 실행 중인 LLM 모델 자체에 숨은 명령을 심을 수 있다는 점에서 '모델 중독' 공격이다. 일단 모델이 중독되면 모든 사용자 프롬프트가 특정 동작을 따르도록 조작될 수 있다.

## 타임라인

- 2026-08-25 [The Hacker News](https://thehackernews.com/2026/08/a-malicious-webpage-could-poison-your.html) — Oasis Security NVIDIA NemoClaw Ollama 제어 취약점 공개

## 관련
