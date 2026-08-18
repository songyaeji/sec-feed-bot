---
slug: dokploy-ownership-privilege-escalation
first_seen: 2026-08-17
tags: [권한상승, PaaS, 조직탈취]
cves: [CVE-2026-45790]
---

# Dokploy — 조직 멤버 초대로 소유권 탈취

자체 호스팅 **Dokploy** PaaS 0.29.6 이전 버전의 organization.inviteMember tRPC 프로시저에서 역할 검증이 부재하다. member:create 권한을 가진 사용자가 소유자(owner) 역할로 계정을 초대할 수 있고, 특권화된 자체 호스팅 사용자는 임의 역할로 계정을 생성할 수 있다. 소유자 역할은 강등 불가능하므로 영구적인 조직 인수(takeover) 공격이 가능하다.

## 타임라인

- 2026-08-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-45790) — CVE-2026-45790 CVSS 8.0 공개, 멤버 초대 권한 검증 우회로 조직 소유권 탈취 취약점 확인
