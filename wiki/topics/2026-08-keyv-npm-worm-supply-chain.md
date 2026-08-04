---
slug: keyv-npm-worm-supply-chain
first_seen: 2026-08-04
tags: [공급망공격, npm, 자격증명탈취, 악성코드]
cves: []
---

**자격증명 탈취 npm 워밍**이 keyv@6.0.0부터 시작되어 Keyv와 Cacheable 네임스페이스를 넘어 78개 패키지명의 353개 버전(SafeDep 기준)으로 확산됐다. Aikido 보고에 따르면 최소 868개 패키지가 영향을 받고 있다. 악성 패키지는 **Claude Code**와 **VS Code 훅**을 설치하여 개발 환경에서 정보를 탈취한다. 2026년 8월 4일 npm 생태계에 광범위한 공급망 공격이 확인됐다.

## 타임라인

- 2026-08-04 [The Hacker News](https://thehackernews.com/2026/08/keyv-linked-npm-worm-poisons-hundreds.html) — Keyv npm 워밍 353개 감염 패키지 확인, 개발자 도구 훅 배포

## 관련
