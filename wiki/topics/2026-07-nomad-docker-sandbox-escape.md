---
slug: nomad-docker-sandbox-escape
first_seen: 2026-07-08
tags: [오케스트레이션, 권한상향]
cves: [CVE-2026-14891]
---

**HashiCorp Nomad/Nomad Enterprise**의 Docker 태스크 드라이버에서 볼륨 바인드 마운트가 비활성화되었을 때도 호스트 경로를 컨테이너에 바인드할 수 있는 샌드박스 탈출 취약점. 작업 제출자가 호스트 파일을 읽고 쓸 수 있게 된다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-14891) — CVE-2026-14891 공개 (CVSS 8.7)
