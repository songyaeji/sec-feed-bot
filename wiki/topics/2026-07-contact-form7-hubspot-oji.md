---
slug: contact-form7-hubspot-oji
first_seen: 2026-07-08
tags: [WordPress, PHP객체인젝션, RCE]
cves: [CVE-2026-49763]
---

**Contact Form 7 Integration for HubSpot** WordPress 플러그인(≤1.3.7) 미인증 PHP 객체 인젝션(PHP Object Injection). 플러그인이 **deserialize()** 함수로 사용자 입력을 직접 처리하면서 악의적 **serialized 객체 전송**으로 PHP 매직 메서드 체인을 통한 **임의 코드 실행** 가능. WordPress 광범위 배포 플러그인의 RCE 취약점.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-49763) — CVE-2026-49763 공개 (CVSS 9.8)

## 관련
