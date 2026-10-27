---
slug: uds-identity-keycloak-auth-bypass
first_seen: 2026-06-05
tags: [UDS, Keycloak, 인증우회, OAuth2]
cves: [CVE-2026-46389]
---

UDS Core Identity 배포의 Keycloak 설정 이미지 v0.11.0~0.26.0에서 client-kubernetes-secret 인증기 로직 오류. 제출한 client_secret이 마운트된 Kubernetes 시크릿으로 오버라이트되어 비교 전에 의도치 않게 교체. 클라이언트 ID와 임의 client_secret으로 OAuth2 토큰 탈취 가능. uds-operator 클라이언트의 경우 다른 클라이언트 변조 가능.

## 타임라인

- 2026-06-05 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46389) — CVE-2026-46389 공개 (CVSS 10.0, v0.26.1에서 패치)
