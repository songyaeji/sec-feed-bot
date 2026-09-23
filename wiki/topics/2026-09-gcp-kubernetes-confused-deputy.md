---
slug: gcp-kubernetes-confused-deputy
first_seen: 2026-09-23
tags: [클라우드보안, 권한상향, 설정오류, 쿠버네티스, GCP]
cves: []
---

Google Cloud **Kubernetes Config Connector**의 혼동 대리자(confused deputy) 결함으로 제한된 권한의 쿠버네티스 사용자가 전체 Google Cloud 조직의 제어권을 획득할 수 있다. YAML 설정 파일 하나로 조직 수준 권한상향 경로가 열린다. Varonis 분석.

## 타임라인

- 2026-09-23 [BleepingComputer](https://www.bleepingcomputer.com/news/security/how-one-kubernetes-yaml-can-hand-over-a-gcp-organization/) — Varonis Kubernetes Config Connector 혼동 대리자 결함 분석, 조직 제어권 획득 경로 공개

## 관련
