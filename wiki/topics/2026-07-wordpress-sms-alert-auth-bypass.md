---
slug: wordpress-sms-alert-auth-bypass
first_seen: 2026-07-28
tags: [WordPress, WooCommerce, 플러그인, 인증우회, 계정탈취]
cves: [CVE-2026-15014]
---

**SMS Alert – SMS & OTP for WooCommerce 플러그인** 3.9.7 이하 버전의 `billing_phone` 파라미터를 통한 **인증 우회 및 계정 탈취 취약점**. `$_SESSION['sa_mobile_verified']` 플래그가 특정 전화번호에 연계되지 않아 공격자가 피해자 계정을 미인증 상태에서 접근 가능. CVSS 9.8, WordPress 관리자 포함 모든 사용자 계정 탈취 가능.

## 타임라인

- 2026-07-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15014) — CVE-2026-15014 공개 (CVSS 9.8, SMS Alert 3.9.7 이하)

## 관련

- [[wordpress-authentication-vulnerabilities]]
