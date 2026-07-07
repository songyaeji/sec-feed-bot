---
slug: 9router-rce
first_seen: 2026-07-07
tags: [취약점, 코드실행, 라우터]
cves: [CVE-2026-59800]
---

**9Router** 라우팅 소프트웨어 0.4.44 이전 버전에서 OS 명령 삽입 취약점 발견. 인증 불필요한 `/api/tunnel/tailscale-install` 엔드포인트의 `sudoPassword` 필드가 검증 없이 command line argument로 전달되면서 임의 명령 실행 가능. 9Router 인스턴스 완전 제어 위험.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59800) — 9Router OS 명령 삽입 취약점 공개 (CVSS 9.8)

## 관련
