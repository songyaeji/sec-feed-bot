---
slug: sssd-ldap-sudo-privesc
first_seen: 2026-07-07
tags: [Linux, 권한상향, LDAP, SSSD]
cves: [CVE-2026-14474]
---

Linux **SSSD(System Security Services Daemon)**의 LDAP sudo 제공자 권한상향 취약점(CVSS 8.8). ldap_sudo_search_base 옵션이 명시적으로 설정되지 않으면 SSSD가 전체 LDAP 디렉터리 트리에서 sudoRole 객체를 검색하므로, LDAP 하위 트리에 쓰기 권한이 있는 인증 공격자가 루트 수준 sudo 권한을 얻을 수 있다.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14474) — CVE-2026-14474 공개

## 관련

[[sssd-ad-gpo-path-traversal]]
