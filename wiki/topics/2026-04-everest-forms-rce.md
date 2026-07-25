---
slug: everest-forms-rce
first_seen: 2026-04-08
tags: [워드프레스플러그인, 역직렬화, RCE]
cves: [CVE-2026-3296]
---

# Everest Forms 플러그인 PHP 객체 주입 RCE

WordPress Everest Forms 플러그인이 폼 엔트리 메타값을 검증 없이 unserialize() 처리. 공개 폼을 통해 악의적 직렬화 객체 주입 가능하며, 관리자가 엔트리 조회시 RCE 발생.

## 타임라인

- 2026-04-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-3296) — CVE-2026-3296 공개 (CVSS 9.8)

## 관련

없음
