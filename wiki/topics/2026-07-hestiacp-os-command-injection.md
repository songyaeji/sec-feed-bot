---
slug: hestiacp-os-command-injection
first_seen: 2026-07-10
tags: [원격코드실행, 호스팅제어판, 권한상향]
cves: [CVE-2025-30007]
---

**HestiaCP** 웹호스팅 제어판(< 1.9.5) 인증된 OS 명령 인젝션 취약점. 저권한 인증 사용자가 DNS 레코드 타입에 따옴표 문자를 삽입해 입력 검증 우회. `is_dns_record_format_valid()` 부재 검증 및 `update_domain_zone()`의 unsafe eval 파싱 결합으로 변수 할당 문자열 조기 종료. **결과: 단일 DNS 레코드 생성으로 root 권한 코드 실행** (CVSS 8.8).

## 타임라인

- 2026-07-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-30007) — CVE-2025-30007 공개

## 관련
