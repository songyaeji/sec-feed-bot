---
slug: socfortress-copilot-stored-xss
first_seen: 2026-10-30
tags: [저장XSS, 권한상향, 보안운영플랫폼]
cves: [CVE-2026-61728]
---

SOCFortress CoPilot의 고객 포털에서 사용자 입력(comment, note 등)을 HTML 이스케이프 없이 v-html로 렌더링해 저장 XSS 공격이 가능하며, 인증 토큰을 JavaScript에서 접근 가능한 위치에 저장해 스크립트 주입으로 고권한 사용자 계정 탈취가 가능하다.

## 타임라인

- 2026-10-30 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-61728) — 저장 XSS 취약점으로 분석가·관리자 계정 탈취 및 권한상향 가능, 버전 0.1.70·0.1.76 이상에서 패치

## 관련

[[socfortress-copilot-path-traversal]]
