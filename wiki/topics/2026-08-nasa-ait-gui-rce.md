---
slug: nasa-ait-gui-rce
first_seen: 2026-08-20
tags: [RCE, NASA, 우주선제어, 미인증공격, 핵심인프라]
cves: [GHSA-p9r8-2q67-fp86]
---

# NASA AIT-GUI — 우주선 제어 명령 원격실행 취약점

NASA/JPL의 AMMOS Instrument Toolkit(AIT) 웹 기반 오퍼레이터 콘솔 **AIT-GUI**에서 중대 취약점이 발견됐다. 미인증 공격자가 우주선 및 도구 제어 버스(spacecraft/instrument command bus)에 임의 명령을 직접 전송할 수 있는 취약점 체인으로, CVSS 9.4로 평가된다. Cycode 연구팀이 공개했으며, 우주선 운영 시스템 직접 영향으로 심각도가 매우 높다.

## 타임라인

- 2026-08-20 [The Hacker News](https://thehackernews.com/2026/08/nasa-ait-gui-flaws-could-let.html) — Cycode 보안 연구팀 AIT-GUI 취약점 공개, GHSA-p9r8-2q67-fp86 (CVSS 9.4)

## 관련
