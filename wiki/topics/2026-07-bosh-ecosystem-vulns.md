---
slug: bosh-ecosystem-vulns
first_seen: 2026-07-09
tags: [BOSH, 권한상향, RCE, 인자주입]
cves: [CVE-2026-47829, CVE-2026-47830, CVE-2026-47831, CVE-2026-47826]
---

BOSH CLI 및 Windows stemcell 빌더에서 4개의 중대 취약점 발견. 정상 SSH 옵션 인자에 임의 옵션 주입, 파일 권한 검증 누락으로 SYSTEM 권한 획득, 약한 난수 생성으로 SSH 접근 가능, 경로 순회로 임의 파일 쓰기. 클라우드 인프라 배포 자동화 도구의 핵심 결함.

## 타임라인

- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-47829) — CVE-2026-47829 (CVSS 8.3) bosh-cli SSH 인자 인젝션
- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-47830) — CVE-2026-47830 (CVSS 8.8) Windows stemcell 파일 덮어쓰기 권한상향
- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-47831) — CVE-2026-47831 (CVSS 7.5) GenerateRandomPassword 약한 난수 생성
- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-47826) — CVE-2026-47826 (CVSS 8.8) blobs.yml 경로 순회 임의 파일 쓰기
