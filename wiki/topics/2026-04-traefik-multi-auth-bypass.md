---
slug: traefik-multi-auth-bypass
first_seen: 2026-04-30
tags: [Traefik, 로드밸런서, 인증우회, 다중취약점]
cves: [CVE-2026-35051, CVE-2026-39858]
---

# Traefik ForwardAuth 미들웨어 인증 우회

**Traefik** v2.11.43, v3.6.14, v3.7.0-rc.2 이전 버전의 **ForwardAuth** 미들웨어에서 발견된 인증 우회 취약점(CVSS 10.0).

**CVE-2026-35051**: trustForwardHeader=false 설정 하에서 신뢰된 업스트림 프록시 뒤에 배포된 경우, 업스트림 프록시 신뢰 컨텍스트를 기반으로 인증을 우회할 수 있다.

**CVE-2026-39858**: ForwardAuth 미들웨어의 정규화 로직이 canonical 헤더명(예: X-Forwarded-Proto)만 제거하고 underscore 별체(예: X_Forwarded_Proto)는 정규화하지 못해, 백엔드가 양쪽 형식을 동등하게 처리할 경우 공격자가 alias 헤더를 통해 신뢰 컨텍스트를 주입하고 인증을 무시할 수 있다.

## 타임라인

- 2026-04-30 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-35051) — CVE-2026-35051 공개 (CVSS 10.0)
- 2026-04-30 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-39858) — CVE-2026-39858 공개 (CVSS 10.0)
