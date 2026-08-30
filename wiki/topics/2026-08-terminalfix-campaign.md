---
slug: terminalfix-campaign
first_seen: 2026-08-28
tags: [ClickFix변종, 역터널백도어, 사회공학]
cves: []
---

**TerminalFix**는 기존 ClickFix 공격을 **Windows Terminal** 또는 **PowerShell**로 확대한 변종 캠페인이다. 가짜 Cloudflare CAPTCHA로 피싱한 뒤 **DLL 사이드로딩**을 활용해 역터널 백도어를 배포하며, 탐지를 우회하는 다단계 침입 체인을 사용한다.

## 타임라인

- 2026-08-28 [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/08/28/terminalfix-campaign-deploys-reverse-tunnel-through-multistage-intrusion/) — ClickFix 변종 TerminalFix 캠페인 분석, 가짜 CAPTCHA로 Terminal/PowerShell 유도 역터널 배포
- 2026-08-30 [The Hacker News](https://thehackernews.com/2026/08/terminalfix-uses-fake-cloudflare.html) — TerminalFix 캠페인 상세 분석 및 완화 방법 공개

## 관련
