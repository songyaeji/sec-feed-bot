---
slug: traefik-k8s-gateway-filter
first_seen: 2026-07-08
tags: [Traefik, 로드밸런서, Kubernetes, Gateway API, RCE]
cves: [CVE-2026-54765]
---

Traefik v3.7.0~v3.7.5의 Kubernetes Gateway API 제공자에서 발생하는 백엔드 필터 처리 결함. 동일한 Service:port를 목표로 하지만 서로 다른 backendRef 필터를 설정한 두 개의 HTTPRoute가 수락될 때, Traefik이 두 경로를 동일한 자식 서비스로 해석하고 하나의 필터만 적용하여 경로 우회 가능. 결과적으로 인가되지 않은 트래픽이 백엔드 서비스에 직접 도달할 수 있음.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54765) — CVE-2026-54765 공개 (CVSS 8.5)
