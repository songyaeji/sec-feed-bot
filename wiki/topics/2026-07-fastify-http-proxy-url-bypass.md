---
slug: fastify-http-proxy-url-bypass
first_seen: 2026-07-18
tags: [프록시우회, 오픈소스라이브러리, 인증우회]
cves: [CVE-2026-16117]
---

@fastify/http-proxy 11.5.0 이하에서 URL 인코딩된 경로로 라우터 검증을 우회할 수 있는 취약점. 프록시의 rewritePrefix 검증이 디코딩된 경로에만 적용되므로 URL 인코딩된 문자를 포함한 요청은 검증을 통과한 후 상위 서버로 원본 인코딩 형태 그대로 전달되어 내부 경로 접근 가능.

## 타임라인

- 2026-07-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16117) — CVE-2026-16117 공개, 11.6.0 업그레이드 권장

## 관련

[[fastify-framework-security]]
