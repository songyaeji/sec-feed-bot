---
slug: bloyal-wordpress-privilege-escalation
first_seen: 2026-08-15
tags: [WordPress, 권한상향, 플러그인, API조작]
cves: [CVE-2026-15001]
---

bLoyal: Loyalty & Promotions by bLoyal WordPress 플러그인 3.1.611.78 이하에서 AJAX 액션들(save_bloyal_configuration_data, save_bloyal_accesskeyverification_data)이 권한/nonce 검사 없이 등록되어, 구독자 이상 인증된 사용자가 bLoyal Loyalty Engine API URL을 공격자 서버로 변조하고 미인증 /cart REST 라우트 호출 시 임의 사용자(관리자 포함) 로그인 가능. CVSS 8.8.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15001) — CVE-2026-15001 공개, API URL 조작을 통한 권한상향 취약점 확인
