---
slug: nginx-http2-vuln
first_seen: 2026-07-08
tags: [NGINX, HTTP/2, RCE]
cves: [CVE-2026-42055]
---

**NGINX** Plus/Open Source의 `ngx_http_proxy_v2_module`과 `ngx_http_grpc_module`에서 HTTP/2 트래픽 프록시 시 `ignore_invalid_headers` 지시어가 off로 설정되었을 때 대형 비표준 헤더 처리로 인한 취약점(CVSS 8.1). RCE 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-42055) — CVE-2026-42055 공개 (CVSS 8.1, RCE)

## 관련
