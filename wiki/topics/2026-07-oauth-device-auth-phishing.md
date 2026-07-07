---
slug: oauth-device-auth-phishing
first_seen: 2026-07-06
tags: [phishing, oauth, account-takeover]
cves: []
---

기업 계정을 탈취하는 신규 피싱 기법. 공격자가 정상적인 **OAuth 2.0 Device Authorization Grant** 인증 흐름(입력 제약 기기 로그인용)을 악용해 비밀번호 탈취 없이 기업 계정을 장악함.

## 타임라인

- 2026-07-06 [GBHackers](https://gbhackers.com/?p=191327) — 일회성 코드를 이용한 기업 계정 피싱 기법 보고
- 2026-07-07 [Cisco Talos](https://blog.talosintelligence.com/artoken-inside-an-eviltokens-affiliate-panel-targeting-microsoft-365/) — ARToken 피싱-as-a-Service 플랫폼 적발, 80+ API 엔드포인트 노출 (Primary Refresh Token 지속성, BEC, SharePoint 유출 기능)

## 관련

