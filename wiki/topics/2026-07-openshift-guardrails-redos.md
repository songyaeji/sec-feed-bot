---
slug: openshift-guardrails-redos
first_seen: 2026-07-08
tags: [AI, 서비스거부]
cves: [CVE-2026-15154]
---

**Red Hat OpenShift AI**의 `guardrails-detectors` 컴포넌트가 공개 API에서 사용자 입력 정규표현식을 충분히 검증하지 않아, 복잡한 패턴으로 인한 과도한 백트래킹(ReDoS)이 발생하여 서비스 거부가 가능한 취약점. 원격 공격자가 특수 제작된 정규표현식으로 플랫폼을 다운시킬 수 있다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15154) — CVE-2026-15154 공개 (CVSS 6.5)
