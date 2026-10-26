---
slug: chrome-sandbox-escape
first_seen: 2026-06-30
tags: [브라우저보안, 메모리취약점, 샌드박스우회]
cves: [CVE-2026-13782]
---

Google Chrome 150 이전 버전의 브라우저 엔진에 use-after-free 취약점이 존재해 렌더러 프로세스를 이미 침해한 공격자가 샌드박스를 우회해 시스템 권한으로 임의 코드 실행이 가능하다.

## 타임라인

- 2026-06-30 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-13782) — CVE-2026-13782 공개, CVSS 10.0, Chromium 중대도 Use-after-free 샌드박스 탈출
