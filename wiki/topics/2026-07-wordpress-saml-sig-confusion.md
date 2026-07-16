---
slug: wordpress-saml-sig-confusion
first_seen: 2026-07-16
tags: [WordPress, 플러그인, SAML, 인증우회, 계정탈취]
cves: [CVE-2026-15013]
---

**WordPress Mo SAML SSO 플러그인** 5.4.3 이하에서 SAMLResponse의 SignatureMethod 속성을 공격자 제어 값으로 직접 읽어, 설정된 서명 알고리즘을 무시한다. IdP의 RSA 공개키를 HMAC-SHA1 공유 암호로 재해석하게 해 SAML assertion 위조가 가능하며, 모든 WordPress 계정(관리자 포함) 탈취 가능(CVSS 9.8).

## 타임라인

- 2026-07-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15013) — CVE-2026-15013 공개
