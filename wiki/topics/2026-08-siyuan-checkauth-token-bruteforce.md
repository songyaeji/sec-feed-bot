---
slug: siyuan-checkauth-token-bruteforce
first_seen: 2026-08-16
tags: [노트앱, RCE, 미인증접근]
cves: [CVE-2026-73056]
---

# SiYuan CheckAuth — 미인증 토큰 무제한 추측 취약점

개인용 노트 앱 **SiYuan** v3.7.4 이전 버전의 CheckAuth() 미들웨어가 API 토큰 인증 시도에 대한 제한(CAPTCHA, 잠금)을 적용하지 않아, 미인증 공격자가 짧거나 약한 토큰을 무제한으로 추측 가능. 성공 시 전체 관리자 권한으로 파일 조작 및 SQL 쿼리 실행.

## 타임라인

- 2026-08-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-73056) — CVE-2026-73056 CVSS 9.8 공개, 토큰 추측 후 관리자 권한 탈취 확인

## 관련

[[siyuan-sql-injection]] — SiYuan 다중 SQL Injection 취약점
