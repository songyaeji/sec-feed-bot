---
slug: wordpress-apt-booking-plugin-rce
first_seen: 2026-07-08
tags: [vulnerability, wordpress-plugin, rce, deserialization]
cves: [CVE-2026-12378]
---

Appointment Booking Calendar Plugin 및 Scheduling Plugin의 PHP 역직렬화 취약점 **CVE-2026-12378** (CVSS 8.1). 플러그인 1.1.28 이하에서 PHP 역직렬화 함수로 전달 전 데이터 검증이 없어, 적절한 가젯 체인이 존재할 경우 미인증 공격자가 임의 PHP 객체를 주입하여 코드 실행 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-12378) — CVE 공개

## 관련

