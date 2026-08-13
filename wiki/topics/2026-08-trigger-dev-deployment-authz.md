---
slug: trigger-dev-deployment-authz
first_seen: 2026-08-13
tags: [AI, 에이전트, 권한우회]
cves: [CVE-2026-73656]
---

Trigger.dev 4.5.5 이하 버전의 POST /api/v1/deployments/:deploymentId/background-workers 엔드포인트에서 environmentId 조건이 없어 한 프로젝트의 API 키로 다른 프로젝트의 배포를 조작할 수 있다. 공격자는 피해자 배포에 공격자 소유의 백그라운드 워커를 링크하여 배포 상태를 조작할 수 있다.

## 타임라인

- 2026-08-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-73656) — CVE-2026-73656 CVSS 9.9 공개, 교차 프로젝트 배포 조작 취약점 확인, 4.5.6에서 수정됨
