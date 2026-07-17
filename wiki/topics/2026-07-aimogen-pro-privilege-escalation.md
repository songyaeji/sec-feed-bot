---
slug: aimogen-pro-privilege-escalation
first_seen: 2026-07-17
tags: [vulnerability, wordpress-plugin, ai-feature]
cves: [CVE-2026-15982]
---

WordPress AI 컨텐츠 작성 플러그인 Aimogen Pro 2.8.4 이하에서 aiomatic_call_google_ai_function 함수의 권한 검증 부재로 인한 권한 상향. 미인증 공격자가 aimogen_wp_god_mode 도구로 함수 블랙리스트를 우회해 임의 PHP 함수를 실행할 수 있다.

## 타임라인

- 2026-07-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15982) — CVE-2026-15982 CVSS 9.8: Aimogen Pro의 aiomatic_call_google_ai_function에 권한 검증 부재, 미인증 공격자가 aimogen_wp_god_mode로 함수 블랙리스트 해제 후 임의 PHP 함수(관리자 계정 생성 포함) 실행 가능

## 관련
