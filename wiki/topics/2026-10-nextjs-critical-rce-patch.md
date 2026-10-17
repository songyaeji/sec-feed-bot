---
slug: nextjs-critical-rce-patch
first_seen: 2026-10-15
tags: [RCE, 웹프레임워크, 긴급패치, SVG처리]
cves: []
---

**Next.js**가 10월 14일 긴급 번외 패치를 발표해 비인증 원격코드실행 2개와 고심각도 거부 서비스 1개를 수정했다. React Server Components 취약점과 **librsvg** 라이브러리(sharp 패키지)의 SVG 처리 취약점이 포함됐다.

## 타임라인

- 2026-10-14 [Vercel/Next.js](https://github.com/vercel/next.js) — 비인증 RCE 2개, 거부 서비스 1개 긴급 패치
- 2026-10-15 [The Hacker News](https://thehackernews.com/2026/10/nextjs-ships-out-of-band-patch-for-two.html) — React Server Components, SVG 처리 RCE 상세 분석

## 관련
