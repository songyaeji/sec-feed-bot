---
slug: wildfly-ejb-vulnerabilities
first_seen: 2026-11-10
tags: [EJB취약점, 엔터프라이즈서버, 인증우회]
cves: [CVE-2026-111264, CVE-2026-87756, CVE-2026-111240]
---

# WildFly — EJB 3개 중대 취약점

애플리케이션 서버 **WildFly** 10.3.0·11.0.0-M2 이전 버전에서 EJB 관련 3개 중대 취약점이 발견됐다. HTTP 메서드 기반 인증 우회, 무인증 원격 배포·코드 실행, NULL 비밀번호 인증 우회가 가능하다.

## 타임라인

- 2026-11-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-111264) — CVE-2026-111264 CVSS 9.8 공개, EJB JAX-WS 엔드포인트 HTTP 메서드 기반 인증 우회 확인
- 2026-11-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-87756) — CVE-2026-87756 CVSS 9.8 공개, 원격 EJB 미인증 배포·명령 실행 확인
- 2026-11-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-111240) — CVE-2026-111240 CVSS 9.8 공개, JDBC JAAS NULL 비밀번호 인증 우회 확인

## 관련
