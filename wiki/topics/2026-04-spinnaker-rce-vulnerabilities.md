---
slug: spinnaker-rce-vulnerabilities
first_seen: 2026-04-20
tags: [CD플랫폼, 원격코드실행, 마이크로서비스, 다중취약점]
cves: [CVE-2026-32604, CVE-2026-32613]
---

# Spinnaker — 다중 원격코드 실행 취약점

오픈소스 멀티클라우드 지속적 배포(CD) 플랫폼 Spinnaker에서 2개의 중대 RCE 취약점이 발견됐다. clouddriver 파드에서 gitrepo artifact 타입으로 임의 명령 실행이 가능하고, Echo 서비스에서 SPeL(Spring Expression Language) 표현식 처리 시 신뢰되지 않은 클래스에 대한 접근 제한이 없어 JVM 명령 실행이 가능하다. 2026.1.0, 2026.0.1, 2025.4.2, 2025.3.2 버전에서 패치됐다.

## 타임라인

- 2026-04-20 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-32613) — CVE-2026-32613 Echo SPeL 표현식 주입, CVSS 9.9
- 2026-04-20 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-32604) — CVE-2026-32604 clouddriver 명령 실행, CVSS 9.9

## 관련
