---
slug: dokploy-multi-rce
first_seen: 2026-08-10
tags: [명령인젝션, RCE, PaaS, 다중취약점]
cves: [CVE-2026-72733, CVE-2026-72735, CVE-2026-72736, CVE-2026-72738, CVE-2026-72740]
---

자체 호스팅 **Dokploy** PaaS 플랫폼 0.29.13 이전 버전에 쉘 명령 인젝션으로 인한 RCE 5개 취약점이 발견됐다. 백업 복구, Traefik 설정 직렬화, 레지스트리 자격증명 테스트, S3 경로 정규화, Git URL 파싱 단계에서 사용자 입력값이 쉘 명령에 직접 보간된다. 모두 인증된 사용자가 호스트 또는 원격 서버 컨텍스트에서 OS 명령을 임의 실행할 수 있는 위험도 높은 취약점이다.

## 타임라인

- 2026-08-10 [NVD CVE-2026-72733](https://nvd.nist.gov/vuln/detail/CVE-2026-72733) — Dokploy backup.restoreBackupWithLogs tRPC 명령 인젝션 CVSS 9.9
- 2026-08-10 [NVD CVE-2026-72735](https://nvd.nist.gov/vuln/detail/CVE-2026-72735) — Dokploy writeTraefikConfigRemote Traefik YAML 직렬화 명령 인젝션 CVSS 9.9 (CVE-2026-45630 불완전 패치)
- 2026-08-10 [NVD CVE-2026-72736](https://nvd.nist.gov/vuln/detail/CVE-2026-72736) — Dokploy 레지스트리 자격증명 테스트·Swarm 클러스터 관리 명령 인젝션 CVSS 9.9
- 2026-08-10 [NVD CVE-2026-72738](https://nvd.nist.gov/vuln/detail/CVE-2026-72738) — Dokploy backup.listBackupFiles S3 경로 검색 명령 인젝션 CVSS 9.9
- 2026-08-10 [NVD CVE-2026-72740](https://nvd.nist.gov/vuln/detail/CVE-2026-72740) — Dokploy customGitUrl SSH 키 설정 ssh-keyscan 명령 인젝션 CVSS 9.9 (모두 0.29.13에서 패치)
