---
slug: axios-no-proxy-bypass
first_seen: 2026-04-09
tags: [JavaScript, HTTP클라이언트, 프록시우회, 인증]
cves: [CVE-2025-62718]
---

# Axios HTTP 클라이언트 NO_PROXY 규칙 우회

Node.js 및 브라우저용 Promise 기반 HTTP 클라이언트 **Axios** 1.15.0 및 0.31.0 이전 버전에서 호스트명 정규화 시 NO_PROXY 규칙 검증을 올바르게 처리하지 않음(CVSS 9.9). localhost.(점), [::1](IPv6 리터럴) 등 루프백 주소로 우회 가능하여 프록시 규칙 우회.

## 타임라인

- 2026-04-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-62718) — CVE-2025-62718: Axios 1.15.0, 0.31.0 이상 버전에서 수정
