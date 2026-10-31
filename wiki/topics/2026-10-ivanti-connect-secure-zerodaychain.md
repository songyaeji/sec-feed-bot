---
slug: ivanti-connect-secure-zerodaychain
first_seen: 2026-10-13
tags: [제로데이, 원격접근가상사설망, 미패치]
cves: [CVE-2026-104935, CVE-2026-111357, CVE-2026-118527]
---

공격자가 Ivanti Connect Secure VPN 어플라이언스의 세 개 제로데이를 체인화해 로그인 없이 루트 권한으로 명령 실행 가능한 취약점을 악용 중이다. 벤더는 두 개에 대한 패치를 공개했으나 세 번째는 아직 패치 대기 중이다.

## 타임라인

- 2026-10-13 [The Hacker News](https://thehackernews.com/2026/10/attacker-chains-three-ivanti-connect.html) — 보안회사 Volexity, 세 개 제로데이 체인화해 루트 명령 실행 공격 발표. Ivanti 두 개만 패치, 세 번째 미패치 상태
- 2026-10-13 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-104935) — CVE-2026-104935 스푸핑을 통한 인증우회 CISA KEV 추가
- 2026-10-14 [CISA](https://www.bleepingcomputer.com/news/security/cisa-warns-admins-to-immediately-fix-ivanti-flaw-exploited-as-zero-day/) — CISA, 관리자에게 10월 1일부터 제로데이 악용 중인 Ivanti 취약점 긴급 패치 경고
- 2026-10-30 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-118527) — CVE-2026-111357, CVE-2026-118527 제로데이 두 개 CISA KEV 추가

## 관련

[[ivanti-sentry-os-command-injection]]
