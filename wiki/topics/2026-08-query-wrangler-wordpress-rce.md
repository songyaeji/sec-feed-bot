---
slug: query-wrangler-wordpress-rce
first_seen: 2026-08-16
tags: [WordPress, RCE, 플러그인취약점]
cves: [CVE-2026-14498]
---

# Query Wrangler WordPress — 미인증 RCE 취약점

**Query Wrangler** 플러그인 1.5.57 이하의 wp_ajax_qw_form_ajax 핸들러가 nonce만 검증하고 capability 체크 없이 wp_ajax_nopriv_에서 등록되어, Subscriber 권한 사용자가 unsanitized attacker-controlled options를 call_user_func_array()에 직접 전달 가능하며, 임의 PHP 함수 호출 및 원격코드 실행 가능.

## 타임라인

- 2026-08-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14498) — CVE-2026-14498 CVSS 8.8 공개, 권한검증 부재로 인한 기능 함수 호출 RCE 확인
