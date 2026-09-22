---
slug: f5-bigip-apm-rce
first_seen: 2026-09-22
tags: [RCE, VPN, authentication, APM]
cves: [CVE-2026-94127]
---

F5 **BIG-IP APM**(Access Policy Manager)의 힙 버퍼 오버플로우 취약점으로 미인증 원격코드실행이 가능하다. 접근정책과 OAuth 프로필이 설정된 가상 서버에서 공격이 성립하며, CISA 시스템에 실제 악용 사례가 등록돼 있다.

## 타임라인

- 2026-09-22 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-94127) — CVE-2026-94127로 공개, 미인증 RCE 취약점으로 CISA 공격자활용목록에 등재
