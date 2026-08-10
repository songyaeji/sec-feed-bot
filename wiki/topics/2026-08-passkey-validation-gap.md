---
slug: passkey-validation-gap
first_seen: 2026-08-03
tags: [인증우회, 무선번호인증, 보안분석, 공격표면]
cves: []
---

Palo Alto Networks Unit 42가 **Passkey** 구현의 보안 결함을 분석했다. 신뢰 당사자(relying parties)가 User Verified 플래그를 적절히 검증하지 못할 경우, 다중인증(MFA)이 사실상 단일 인증 요소로 축소될 수 있다. 비밀번호 없는 인증으로의 전환 과정에서 구현 오류가 보안을 약화시킬 위험을 드러낸다.

## 타임라인

- 2026-08-03 [Unit 42](https://unit42.paloaltonetworks.com/passwordless-authentication-security-risks/) — Pass the Passkey: A Novel Attack Surface in Passwordless Authentication
- 2026-08-03 [The Hacker News](https://thehackernews.com/2026/08/google-password-manager-attacks-could.html) — Google Password Manager **Pass-ta-key** 공격: Passkey 클라우드 인증기 3가지 악용 경로 분석
- 2026-08-10 [The Hacker News](https://thehackernews.com/2026/08/new-passkey-attacks-can-recover-synced.html) — 3개 독립 연구팀, 동기화 개인키 탈취·피싱저항 MFA 우회 새로운 Passkey 공격 공개

## 관련

[[ai-voice-clone-finance-auth-bypass]] — AI 음성 복제로 금융 거래 승인 우회
