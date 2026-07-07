---
slug: sssd-ad-gpo-path-traversal
first_seen: 2026-07-07
tags: [Linux, LDAP, 경로이동, 권한상향]
cves: [CVE-2026-14476]
---

**SSSD**의 Active Directory GPO 제공자 경로이동 취약점(CVSS 8.0). ad_gpo_extract_smb_components() 함수가 gPCFileSysPath LDAP 속성의 `..` 시퀀스를 검증하지 않아, AD GPO 관리 권한을 가진 공격자가 GPO 캐시 디렉터리 밖에 루트 권한으로 파일을 작성할 수 있다. Red Hat 기본 설정에서 특히 심각한 영향.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14476) — CVE-2026-14476 공개

## 관련

[[sssd-ldap-sudo-privesc]]
