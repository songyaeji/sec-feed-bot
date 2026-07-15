---
slug: traefik-http3-mtls-bypass
first_seen: 2026-07-15
tags: [인증우회, 클라우드보안, 로드밸런서]
cves: [CVE-2026-53622]
---

**Traefik** 3.7.3 이전 버전에서 HTTP/3(QUIC) TLS 설정 선택의 결함으로 인해 미인증 클라이언트가 라우터별 **mTLS 강제 정책을 우회**할 수 있다. SNI 값의 대소문자 민감한 정확 매칭이 와일드카드 패턴(*.example.com)을 인식하지 못해, TLS 핸드셰이크 시 기본 TLS 설정으로 폴백되고, 클라이언트 인증서 없이도 통신이 가능해진다.

## 타임라인

- 2026-06-23 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53622) — CVE-2026-53622 공개, Traefik 3.7.3에서 수정

## 관련

[[traefik-k8s-gateway-filter]]
