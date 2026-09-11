---
slug: jfrog-artifactory-auth-bypass
first_seen: 2026-09-01
tags: [원격코드실행, 공급망공격]
cves: [CVE-2026-82329]
---

**JFrog Artifactory**의 인증 우회 취약점(CVE-2026-82329, CVSS 9.8)이 공개 후 며칠 만에 공격자들에게 적극 악용되고 있다. 기본 설정 상태에서 인증 없이 관리자 토큰을 발급받아 전체 시스템을 제어할 수 있으며, 배포 파이프라인 오염을 통한 공급망 공격의 관문이 될 수 있다.

## 타임라인

- 2026-09-01 [The Hacker News](https://thehackernews.com/2026/09/attackers-exploit-critical-jfrog.html) — CVE-2026-82329 공개 후 공격자들이 이미 악용 중임 확인
- 2026-09-11 [The Hacker News](https://thehackernews.com/2026/09/attackers-chain-jfrog-artifactory-flaws.html) — Wiz, 2개 Artifactory 취약점 연쇄 악용으로 관리자 권한 탈취·백도어 설치 실제 공격 확인 (8월 15일~9월 8일)
- 2026-09-11 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-42018) — CVE-2026-42018 인증 우회 취약점 공개, 미인증 호출자에게 익명 토큰 반환
