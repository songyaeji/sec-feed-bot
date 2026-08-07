---
slug: chaindrop-npm-propagating-malware
first_seen: 2026-08-04
tags: [공급망공격, npm, 자체전파, 악성패키지]
cves: []
---

**ChainDrop** 자체 전파 악성코드가 npm 레지스트리의 **1,300개 이상 패키지**(월 누적 다운로드 20억 건)를 침해했다. 다양한 조직의 네임스페이스에 걸쳐 확산되었으며, 웜 특성으로 감염된 패키지에서 추가 패키지로 자동 전파된다. npm 공급망에 대규모 영향을 미치는 심각한 사건이다.

## 타임라인

- 2026-08-04 [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/08/04/chaindrop-supply-chain-compromise-anatomy-self-propagating-worm/) — ChainDrop 자체 전파 워밍 자동 재발행으로 소프트웨어 생태계 확산 공격 체인 상세 분석
- 2026-08-04 [BleepingComputer](https://www.bleepingcomputer.com/news/security/massive-chaindrop-npm-supply-chain-attack-infects-hundreds-of-packages/) — ChainDrop npm 공급망 공격 1,300개 패키지 침해 확인
- 2026-08-06 [Palo Alto Networks Unit 42](https://unit42.paloaltonetworks.com/chaindrop-npm-worm-analysis/) — ChainDrop npm 워밍 동작 원리 및 GitHub Actions 악용 실행 체인 분석

## 관련
