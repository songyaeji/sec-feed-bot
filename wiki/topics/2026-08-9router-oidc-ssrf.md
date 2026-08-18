---
slug: 9router-oidc-ssrf
first_seen: 2026-08-17
tags: [SSRF, AI라우터, 내부서비스스캔, 정보유출]
cves: [CVE-2026-56677]
---

# 9Router — OIDC 테스트 SSRF 내부 서비스 스캔

AI 라우터 **9Router** 0.5.4 이전 버전의 인증 없는 POST /api/auth/oidc/test 엔드포인트에서 SSRF 취약점이 발견됐다. src/app/api/auth/oidc/test/route.js가 사용자 제어 issuerUrl 파라미터를 fetchOidcDiscovery()에 전달할 때 프라이빗 또는 루프백 대상 제한이 없다. 대시보드 로그인이 비활성화된 경우 미인증 공격자가 내부 서비스를 스캔하고 token_endpoint, jwks_uri 등 OIDC 설정 필드를 탈취할 수 있다.

## 타임라인

- 2026-08-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-56677) — CVE-2026-56677 CVSS 8.6 공개, OIDC 테스트 SSRF 취약점 확인
