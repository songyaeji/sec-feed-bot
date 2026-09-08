---
slug: freeipa-kerb-cred-creation
first_seen: 2026-09-08
tags: [FreeIPA, Kerberos, 인증]
cves: []
---

Red Hat FreeIPA 도메인 인증 시스템에서 미인증 클라이언트가 Kerberos 자격증명을 임의로 생성해 관리자 그룹에 진입할 수 있는 취약점. 두 개의 서로 다른 결함이 연쇄 악용되며, 389 Directory Server의 LDAP 데이터베이스 접근 권한이 필요함.

## 타임라인

- 2026-09-08 [The Hacker News](https://thehackernews.com/2026/09/freeipa-flaw-chain-lets-anonymous.html) — Red Hat 보안 권고 발표
