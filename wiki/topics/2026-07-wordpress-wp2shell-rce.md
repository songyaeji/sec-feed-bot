---
slug: wordpress-wp2shell-rce
first_seen: 2026-07-17
tags: [취약점, WordPress, RCE]
cves: [CVE-2026-60137, CVE-2026-63030]
---

**wp2shell** 취약점은 WordPress 핵심에 있는 미인증 임의 코드 실행 결함으로, 플러그인 미설치 기본 설치도 영향받는다.

## 타임라인

- 2026-07-17 [The Hacker News](https://thehackernews.com/2026/07/new-wp2shell-wordpress-core-flaw-lets.html) — Assetnote 분석, WordPress 6.9·7.0 핵심 RCE 결함 발견, 금요일 강제 자동업데이트로 6.9.5·7.0.2 배포
- 2026-07-18 [BleepingComputer](https://www.bleepingcomputer.com/news/security/wordpress-core-wp2shell-rce-flaws-get-public-exploits-patch-now/) — wp2shell RCE 공개 익스플로잇 공개, 즉시 패치 필요
- 2026-07-21 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-60137) — CVE-2026-60137: WordPress Core SQL 인젝션, CVE-2026-63030과 연쇄로 미인증 RCE 달성
- 2026-07-21 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-63030) — CVE-2026-63030: WordPress Core 해석 충돌 취약점, SQL 인젝션과 연쇄

## 관련
