---
slug: kubernetes-strimzi-cross-tenant-rce
first_seen: 2026-10-20
tags: [원격코드실행, 클라우드인프라, 멀티테넌트]
cves: [CVE-2026-105312]
---

**Strimzi** Operator의 Console 커스텀 리소스에서 테넌트 권한 경계 우회 취약점이 발견되었다. Kubernetes 테넌트가 Console 생성 권한을 가졌다면 임의의 컨테이너 이미지를 배포하고, 할당된 ServiceAccount 권한으로 다른 테넌트의 Kafka 사용자 정보를 읽고 쓸 수 있다. CVSS 9.9 심각도.

## 타임라인

- 2026-10-20 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-105312) — CVE-2026-105312 발표, Strimzi Console 리소스 ServiceAccount 권한 임용 부실로 테넌트 간 경계 침투 (CVSS 9.9)

## 관련

[[kubernetes-security]]
[[cloud-multi-tenant-risks]]
