---
slug: mikrotik-ssh-zerodday
first_seen: 2026-09-02
tags: [제로데이, RCE, 라우터, 인증우회, 활성악용]
cves: []
---

MikroTik RouterOS의 SSH 서비스에 사전 인증 취약점(MikroTrick 체인)이 발견되었다. 공격자는 관리자 자격증명 없이 원격 명령을 실행할 수 있으며, 2026년 9월 2일부터 실제 악용이 진행 중이다. 즉시 패치가 권장된다.

## 타임라인

- 2026-09-23 [The Hacker News](https://thehackernews.com/2026/09/mikrotrick-chain-let-attackers-take.html) — CERT Polska MikroTrick 명명, CVE-2026-67279·CVE-2026-86060 체인 공격 구체화
- 2026-09-24 [Security Affairs](https://securityaffairs.com/199678/hacking/ai-helps-uncover-mikrotrick-attack-chain-in-mikrotik-routeros.html) — AI 도구 활용해 MikroTrick 공격 체인 며칠 내 발견, 두 취약점 연쇄 메커니즘 규명
- 2026-09-06 [Security Affairs](https://securityaffairs.com/198538/security/your-mikrotik-router-may-already-be-compromised-look-for-ssh-user-2.html) — MikroTik RouterOS SSH 제로데이 MikroTrick 활성 악용 중, 패치 권장

## 관련

없음
