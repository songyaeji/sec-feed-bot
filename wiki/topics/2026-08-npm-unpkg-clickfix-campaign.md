---
slug: npm-unpkg-clickfix-campaign
first_seen: 2026-08-25
tags: [공급망공격, npm패키지, CDN악용, 피싱인프라]
cves: []
---

# npm 24개 패키지 — unpkg 미러 악용 ClickFix 피싱

사이버 보안 연구진이 **unpkg CDN 미러**를 악용해 **ClickFix** 스타일의 가짜 Cloudflare CAPTCHA 페이지로 리다이렉트하는 24개의 npm 패키지 캠페인을 공개했다. 개별 패키지는 단순 HTML 페이지만 포함해 설치 자체는 무해하지만, npm 리포지터리를 피싱 인프라로 전환하는 기법이다.

## 타임라인

- 2026-08-25 [The Hacker News](https://thehackernews.com/2026/08/24-npm-packages-abuse-unpkg-mirrors-to.html) — 24개 npm 패키지가 unpkg로 ClickFix 가짜 CAPTCHA 페이지 호스팅

## 관련
