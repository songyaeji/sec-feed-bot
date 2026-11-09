---
slug: openam-saml-auth-bypass
first_seen: 2026-11-08
tags: [인증우회, SAML, SSO침해, CVE-2026-123550]
cves: [CVE-2026-123550]
---

**OpenAM** 16.1.4 이전의 SAML v2.0 서비스 제공자에서 WantAssertionsSigned가 거짓일 때 미서명 어설션을 수용하는 인증 우회 취약점이 발견되었다. 미인증 원격 공격자가 위조된 SAML 어설션을 제출해 임의 사용자로 세션을 획득하고, 종속 SSO 애플리케이션을 장악할 수 있다.

## 타임라인

- 2026-11-08 [NVD CVE-2026-123550](https://nvd.nist.gov/vuln/detail/CVE-2026-123550) — OpenAM 16.1.4 이전 SAML v2.0 미서명 어설션 수용 인증우회 CVSS 9.8
