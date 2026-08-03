---
slug: huggingface-diffusers-rce
first_seen: 2026-08-03
tags: [AI공급망, 원격코드실행, 오픈소스, 모델저장소, 취약점]
cves: []
---

**Hugging Face**의 **Diffusers** 라이브러리에 3개의 높은 심각도 보안 결함이 발견되었다. 공격자는 악의적으로 조작된 모델 저장소를 통해 신뢰 검증(**trust_remote_code**)을 우회하고 임의 코드를 실행할 수 있다. 이는 모델을 로드하는 기계 위에서 직접 실행되어 AI 공급망의 광범위한 보안 위험을 노출시킨다.

## 타임라인

- 2026-08-03 [The Hacker News](https://thehackernews.com/2026/08/hugging-face-diffusers-flaws-could-let.html) — Hugging Face Diffusers 3개 높은 심각도 취약점 공시

## 관련

[[fakegit-smartloader]] — GitHub 저장소 악용 공급망 공격
[[google-opensource-supply-chain-guidance]] — 공개소스 공급망 공격 방어 지침
