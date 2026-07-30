---
slug: argo-workflows-pod-rce
first_seen: 2026-07-16
tags: [Argo, Kubernetes, 오케스트레이션, RCE]
cves: [CVE-2026-31892, CVE-2026-54526]
---

**Argo Workflows**의 allow-list 검증 불완전으로 인한 임의 pod 명령 인젝션 취약점. CVE-2026-31892의 우회 버전으로 3.7.15 이전, 4.0.6 이전 버전이 영향받는다. CVSS 9.9로 평가되며 templateReferencing Strict/Secure 모드에서도 exploitable하다.

## 타임라인

- 2026-07-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54526) — CVE-2026-54526: CVE-2026-31892 우회 pod spec patch 인젝션 (CVSS 9.9)
