---
slug: froxlor-symlink-privilege-escalation
first_seen: 2026-10-20
tags: [권한상향, 웹호스팅, 설정오류]
cves: [CVE-2026-113678]
---

**Froxlor** 2.3.15 미만 버전의 Statistics::makeChownWithNewStats 함수가 심링크를 추적하는 취약점이 발견되었다. 인증 고객이 문서 루트의 goaccess 통계 디렉터리를 심링크로 교체하면, root 권한으로 실행되는 주기적 cron 작업의 chown 명령이 임의 디렉터리의 소유권을 고객에게 이전한다. CVSS 9.9 심각도.

## 타임라인

- 2026-10-20 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-113678) — CVE-2026-113678 발표, Froxlor Statistics 심링크 추적 루트 권한 상향 (CVSS 9.9)

## 관련

[[web-hosting-vulnerabilities]]
[[privilege-escalation-symlink]]
