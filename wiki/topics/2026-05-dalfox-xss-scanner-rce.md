---
slug: dalfox-xss-scanner-rce
first_seen: 2026-05-27
tags: [Dalfox, 보안도구, RCE, 명령인젝션]
cves: [CVE-2026-45087]
---

오픈소스 XSS 스캐너 Dalfox v2.13.0 이전 REST API 서버 모드에서 FoundAction 및 FoundActionShell이 미검증 JSON에서 역직렬화. 미인증 POST /scan으로 임의 명령 실행. 기본 포트 0.0.0.0:6664 API 키 미설정.

## 타임라인

- 2026-05-27 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-45087) — CVE-2026-45087 공개 (CVSS 10.0, v2.13.0에서 패치)
