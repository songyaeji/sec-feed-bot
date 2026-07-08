---
slug: openssh-gssapi-config
first_seen: 2026-07-08
tags: [OpenSSH, GSSAPI, 인증]
cves: [CVE-2026-59998]
---

OpenSSH 10.4 이전 버전에서 Windows Active Directory 환경에서 **GSSAPIStrictAcceptorCheck** 설정이 무효화되는 문서화되지 않은 보안 동작. 인증 검증이 약해져 수용자 검증(Acceptor Check) 보안 메커니즘이 작동하지 않을 수 있음.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59998) — CVE-2026-59998: GSSAPI 설정 무효화 (CVSS 4.8)

## 관련
