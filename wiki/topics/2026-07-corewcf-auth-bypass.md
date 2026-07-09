---
slug: corewcf-auth-bypass
first_seen: 2026-07-08
tags: [CoreWCF, 인증우회, 권한검증]
cves: [CVE-2026-54776, CVE-2026-54778, CVE-2026-54783, CVE-2026-54784, CVE-2026-54772, CVE-2026-54779]
---

CoreWCF 1.8.1과 1.9.1 이전 버전에서 여러 인증·권한 검증 결함 발견. UnixDomainSocket, WS-Security, SAML, 토큰 재생 방지 등 다양한 영역에서 우회 공격 가능. 로컬 권한상향과 원격 인증 무시가 포함됨.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54776) — CVE-2026-54776 (CVSS 4.4) PosixIdentity 스트림 업그레이드 우회
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54778) — CVE-2026-54778 (CVSS 6.2) POSIX ID 조회 비재진입성 경합조건
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54783) — CVE-2026-54783 (CVSS 7.4) WS-Security 서명 검증 우회
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54784) — CVE-2026-54784 (CVSS 7.4) SPNEGO 증거 키 노출
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54772) — CVE-2026-54772 (CVSS 7.5) NetTcpBinding 시작 단계 거부 서비스
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54779) — CVE-2026-54779 (CVSS 5.9) SAML 토큰 재생 방지 비활성화

## 관련

- [[corewcf-namedpipe-interception]]
