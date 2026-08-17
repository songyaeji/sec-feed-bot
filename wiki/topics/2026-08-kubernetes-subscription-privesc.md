---
slug: kubernetes-subscription-privesc
first_seen: 2026-08-17
tags: [Kubernetes, 권한상향, 멀티클라우드, RBAC]
cves: [CVE-2026-66792]
---

# Multicloud Operators Subscription — 권한상향

Red Hat의 **multicloud-operators-subscription** 컴포넌트에서 관리 클러스터 사용자가 특정 주석이 포함된 Subscription 객체를 생성해 권한상향이 가능함(CVSS 9.9). 컨트롤러 Service Account의 권한으로 임의 네임스페이스에 리소스 배포 가능.

## 타임라인

- 2026-08-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-66792) — CVE-2026-66792 공개 권한상향 취약점
