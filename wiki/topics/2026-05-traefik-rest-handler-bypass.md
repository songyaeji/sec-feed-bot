---
slug: traefik-rest-handler-bypass
first_seen: 2026-05-15
tags: [Traefik, 로드밸런서, Kubernetes, REST, 권한우회]
cves: [CVE-2026-44774]
---

# Traefik REST 제공자 노출 취약점

**Traefik** v2.11.46, v3.6.17, v3.7.1 이전 버전의 Kubernetes Gateway API 제공자에서 발생하는 취약점. HTTPRoute 생성 권한을 가진 테넌트가 REST 제공자 핸들러를 노출시킬 수 있으며, providers.rest.insecure=false 설정도 무효화 가능. **CVSS 9.9** 심각 취약점.

## 타임라인

- 2026-05-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44774) — CVE-2026-44774 공개 (CVSS 9.9)
