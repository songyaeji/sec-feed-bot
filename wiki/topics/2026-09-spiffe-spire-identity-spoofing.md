---
slug: spiffe-spire-identity-spoofing
first_seen: 2026-09-10
tags: [Kubernetes, 정체성위조, 후익스플로잇]
cves: []
---

**Unit 42**(Palo Alto Networks)가 Kubernetes 환경에서 **SPIFFE/SPIRE** 신원 관리 프레임워크의 사후 악용 취약점을 분석했다. 노드에 대한 root 접근을 획득한 공격자가 SPIFFE/SPIRE 메타데이터를 악용해 동시 배포 워크로드의 정체성을 위조·수집할 수 있어 마이크로서비스 침해의 첫걸음이 된다.

## 타임라인

- 2026-09-10 [Unit 42](https://unit42.paloaltonetworks.com/kubernetes-spiffe-spire-identity-spoofing/) — K8s SPIFFE/SPIRE 메타데이터 악용해 워크로드 정체성 위조·수집 가능

## 관련
