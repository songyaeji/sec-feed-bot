---
slug: coder-azure-identity-bypass
first_seen: 2026-07-07
tags: [development platform, certificate validation bypass, Azure]
cves: [CVE-2026-46354]
---

Coder 플랫폼의 Azure 신원 인증 검증 부재 취약점. azureidentity.Validate() 함수가 PKCS#7 서명 자체를 검증하지 않고 인증서 체인만 확인. 악의적 PKCS#7 구조로 위변조된 토큰 사용 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46354) — CVE-2026-46354 공개, 여러 버전 영향 (CVSS 9.1)
