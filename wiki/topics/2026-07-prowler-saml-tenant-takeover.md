---
slug: prowler-saml-tenant-takeover
first_seen: 2026-07-10
tags: [인증우회, 테넌트손상, SaaS, 클라우드보안]
cves: [CVE-2026-59151]
---

**Prowler** 클라우드 보안 플랫폼(< 5.30.3) SAML 인증 우회 취약점. SAML 응답에서 주장된 이메일 도메인을 신뢰하고, 토큰 발급 시 검증된 SAML 설정이 아닌 `user.email`에서 테넌트를 재계산. 공격자가 제어하는 SAML IdP에서 한 도메인의 정상 SAML 플로우 완료 후 다른 도메인의 이메일을 주장. **결과: 잘못된 테넌트용 SAMLToken 및 JWT 발급으로 테넌트간 계정 탈취** (CVSS 9.6). 수정본: 5.30.3.

## 타임라인

- 2026-07-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59151) — CVE-2026-59151 공개

## 관련
