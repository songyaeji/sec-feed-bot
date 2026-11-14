---
slug: opstree-buildpiper-privilege-escalation
first_seen: 2026-11-13
tags: [권한상향, Kubernetes, 정책우회, 클러스터관리자]
cves: [CVE-2026-127073, CVE-2026-127080]
---

**OpsTree BuildPiper** 2.7.0 미만에서 2개의 중대 취약점으로 프로젝트 사용자 또는 배포 사용자가 Kubernetes 클러스터 전체 제어 권한 획득 가능. ① 제약 없는 매니페스트 제출로 ClusterRoleBinding 생성해 cluster-admin 권한 탈취, ② 호스트패스 볼륨 마운트로 노드 루트 파일시스템 읽기-쓰기 접근으로 클러스터 자격증명 탈취.

## 타임라인

- 2026-11-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-127073) — CVE-2026-127073 BuildPiper 제약없는 매니페스트 ClusterRoleBinding 권한상향 (CVSS 9.9)
- 2026-11-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-127080) — CVE-2026-127080 BuildPiper hostPath 볼륨 마운트 노드 제어 (CVSS 9.9)

## 관련

[[kyverno-authorization-bypass]]
