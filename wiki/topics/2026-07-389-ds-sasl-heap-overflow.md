---
slug: 389-ds-sasl-heap-overflow
first_seen: 2026-07-07
tags: [LDAP, 디렉터리서버, 버퍼오버플로우]
cves: [CVE-2026-11610]
---

**389 Directory Server(389-ds-base)**의 SASL I/O 계층 힙 버퍼 오버플로우 취약점(CVSS 8.8). SASL 바인드 후 보안 서비스 플래그(SSF > 0) 활성화 상태에서 특수 제작된 LDAP UNBIND 패킷이 512바이트 힙 수신 버퍼로 복사되면서 오버플로우 발생. 인증된 공격자에 의한 원격 코드 실행 위험.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-11610) — CVE-2026-11610 공개

## 관련
