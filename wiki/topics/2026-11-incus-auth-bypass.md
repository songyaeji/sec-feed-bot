---
slug: incus-auth-bypass
first_seen: 2026-11-18
tags: [auth-bypass, container, trust-store]
cves: [CVE-2026-130778]
---

Incus 7.6.0 이전의 TLS 클라이언트 인증서 체인 위조 취약점. 공격자가 신뢰 인증서를 클라이언트 체인에 추가해 클러스터 수준의 접근 권한 획득, 인증 우회, 신뢰 저장소 변조 가능.

## 타임라인

- 2026-11-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-130778) — CVE-2026-130778 CVSS 10.0 공개
