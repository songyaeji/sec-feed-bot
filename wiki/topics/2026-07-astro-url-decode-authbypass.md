---
slug: astro-url-decode-authbypass
first_seen: 2026-07-08
tags: [웹프레임워크, 인증우회]
cves: [CVE-2026-59731]
---

**Astro** 웹 프레임워크 6.4.7에서 URL 디코딩 순서 오류로 인한 인증 우회. 권한 검사는 반복 URL 디코더 한계에 도달한 부분 디코딩된 경로명으로 수행하지만, 이후 경로 재쓰기 규칙 매칭은 추가 `decodeURI()` 작업 실행. 공격자가 인코딩/더블 인코딩된 경로를 조작하여 **보호된 라우트에 우회 접근** 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59731) — CVE-2026-59731 공개 (CVSS 8.2)

## 관련
