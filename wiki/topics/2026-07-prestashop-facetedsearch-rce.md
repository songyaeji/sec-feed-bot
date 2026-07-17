---
slug: prestashop-facetedsearch-rce
first_seen: 2026-07-17
tags: [vulnerability, ecommerce, deserialization-rce]
cves: [CVE-2026-54159]
---

PrestaShop 레이어드 필터 모듈 ps_facetedsearch 3.0.0~4.0.4에서 URL 슬라이더 필터값 검증 부재로 인한 원격 코드 실행. 공격자가 악의적 PHP 직렬화 객체를 주입하면 gadget chain을 통해 웹셸을 배포할 수 있다.

## 타임라인

- 2026-07-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54159) — CVE-2026-54159 CVSS 10.0: ps_facetedsearch의 Content-Disposition 헤더 슬라이더 값 unserialize() 검증 부재, 공격자가 PHP 객체 injection으로 웹셸 배포 후 서버 명령 실행 가능

## 관련
