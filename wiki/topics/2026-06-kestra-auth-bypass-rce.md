---
slug: kestra-auth-bypass-rce
first_seen: 2026-06-26
tags: [워크플로우엔진, 인증우회, RCE, 호스트침해]
cves: [CVE-2026-53576]
---

**Kestra** OSS 1.0.45·1.3.21 이전 버전의 REST API 인증 필터(@Filter("/api/v1/**"))가 경로 끝이 /configs인 모든 요청을 공개 instance-config 엔드포인트로 취급해 자격증명 검사를 우회한다. 미인증 공격자가 Shell·Process 태스크 포함 워크플로우를 생성·실행하고, 공식 docker-compose에서 /var/run/docker.sock 마운트 시 호스트 Docker 데몬 접근 가능.

## 타임라인

- 2026-06-26 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53576) — CVE-2026-53576 공개, CVSS 10.0, REST API 경로 기반 인증 우회
