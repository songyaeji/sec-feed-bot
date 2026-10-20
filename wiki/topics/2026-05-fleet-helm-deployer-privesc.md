---
slug: fleet-helm-deployer-privesc
first_seen: 2026-05-13
tags: [권한상향, 클라우드인프라, 설정오류]
cves: [CVE-2026-41050]
---

**Fleet**의 Helm deployer가 ServiceAccount 권한 가장(impersonation)을 두 코드 경로에서 불완전하게 적용했다. GitRepo 모니터링 저장소에 push 권한을 가진 테넌트는 모든 다운스트림 클러스터의 모든 네임스페이스에서 비밀 정보를 읽을 수 있다. CVSS 9.9 심각도.

## 타임라인

- 2026-05-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-41050) — CVE-2026-41050 발표, Fleet Helm deployer ServiceAccount 권한 미적용으로 다중 클러스터 비밀 노출

## 관련

[[gitops-security]]
[[kubernetes-rbac-flaws]]
