---
slug: tekton-pipelines-path-traversal
first_seen: 2026-03-24
tags: [CI/CD, Kubernetes, 경로순회, RCE]
cves: [CVE-2026-33211]
---

# Tekton Pipelines 경로 순회 원격 코드 실행

Kubernetes 스타일 CI/CD 파이프라인 **Tekton Pipelines** 1.0.0~1.10.2 버전에서 git resolver의 `pathInRepo` 매개변수를 통한 경로 순회 취약점(CVSS 9.6). 테넌트 권한의 공격자가 임의 경로 접근으로 원격 코드 실행 가능.

## 타임라인

- 2026-03-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-33211) — CVE-2026-33211: Tekton 1.0.1, 1.3.3, 1.6.1, 1.9.2, 1.10.2 이상 버전에서 수정
