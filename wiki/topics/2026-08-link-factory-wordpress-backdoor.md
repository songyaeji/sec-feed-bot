---
slug: link-factory-wordpress-backdoor
first_seen: 2026-08-13
tags: [WordPress, 백도어, 플러그인]
cves: [CVE-2026-15413]
---

Link Factory WordPress 플러그인이 백도어로 드러났다. 홈페이지 문장 퍼블리셔로 위장되어 배포되지만, 연산자 제어 REST API가 /wp-json/link-factory/v1/ 하에 노출되며 하드코딩된 Ed25519 공개키로 서명을 검증한다 (헬스체크 제외).

## 타임라인

- 2026-08-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15413) — CVE-2026-15413 CVSS 10.0 공개, 백도어 성질의 악성 플러그인 확인

## 관련

- [[wp-base-booking-rce]]
