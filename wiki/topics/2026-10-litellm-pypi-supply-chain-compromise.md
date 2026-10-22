---
slug: litellm-pypi-supply-chain-compromise
first_seen: 2026-10-21
tags: [AI공급망공격, 파이썬패키지, 악성코드배포, 자격증명탈취]
cves: []
---

LiteLLM Python 패키지 1.107.0 버전이 공급망 공격으로 손상되어 자격증명 탈취기와 백도어를 포함한 악성 코드로 배포됐다. SafeDep, Socket, StepSecurity, Upwind 등 여러 보안 업체가 공동 보도했으며, PyPI와 Docker Hub를 통해 배포된 후 현재 PyPI에서 격리됐다.

## 타임라인

- 2026-10-21 [The Hacker News](https://thehackernews.com/2026/10/litellm-compromised-in-supply-chain.html) — LiteLLM 1.107.0 PyPI wheels·Docker 이미지 공급망 공격, 자격증명 탈취기·백도어 배포, PyPI 격리
- 2026-10-22 [BleepingComputer](https://www.bleepingcomputer.com/news/security/litellm-release-pipeline-hacked-to-distribute-info-stealer-malware/) — 멀웨어 배포 분석 재확인

## 관련

[[malicious-litellm-pypi-supply-chain]]
