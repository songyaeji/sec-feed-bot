---
slug: nvidia-aistore-kubernetes-rce
first_seen: 2026-10-13
tags: [AI인프라보안, Kubernetes보안, 권한상향취약점]
cves: [CVE-2026-65162]
---

**NVIDIA AIStore** for Linux의 legacy ETL Kubernetes PodSpec 초기화 API에서 호스트 네임스페이스와 컨테이너 보안 설정 미검증으로 원격 공격자가 코드 실행, 권한상향, 정보노출, 데이터 변조가 가능하다. AI 모델 학습 인프라를 직접 위협한다.

## 타임라인

- 2026-10-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-65162) — CVE-2026-65162 공개, NVIDIA AIStore Kubernetes API 권한상향 (CVSS 10.0)

## 관련

없음
