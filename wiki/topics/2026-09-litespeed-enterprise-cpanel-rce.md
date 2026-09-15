---
slug: litespeed-enterprise-cpanel-rce
first_seen: 2026-09-15
tags: [공유호스팅, RCE, 권한상향, 웹서버]
cves: []
---

# LiteSpeed Enterprise cPanel 공유 호스팅 권한상향 RCE

cPanel의 LiteSpeed Web Server Enterprise에 치명적 취약점이 발견되었다. 공유 호스팅 환경에서 낮은 권한 웹사이트 사용자가 CageFS 격리를 우회하여 루트 권한을 획득할 수 있다. 같은 서버에 수십 개 이상의 고객 사이트가 호스팅되는 환경에서 한 계정의 공격자가 다른 사이트와 서버 전체에 접근·변조할 수 있는 위험성이 있다. 7월 버전 6.3.7로 강제 업데이트 필수.

## 타임라인

- 2026-09-15 [Security Affairs](https://securityaffairs.com/199127/security/shared-hosting-at-risk-litespeed-enterprise-bug-can-grant-root-from-a-single-tenant.html) — cPanel 경고 공식 발표, 루트 권한 획득 경로 및 패치 버전 공지
- 2026-09-15 [The Hacker News](https://thehackernews.com/2026/09/litespeed-enterprise-flaw-could-let-one.html) — 취약점 상세 분석 및 영향 범위 설명

## 관련

[[cpanel-domain-addon-rce]]
