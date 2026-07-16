---
slug: mysterium-node-authbypass
first_seen: 2026-07-08
tags: [Mysterium, 노드관리, 인증우회, 설정변조]
cves: [CVE-2026-31309]
---

**Mysterium Node** v1.36.0 이전 버전의 `/tequilapi/config/user` 엔드포인트가 미인증 접근을 허용해, 공격자가 노드 설정을 임의로 변경하고 완전한 노드 탈취가 가능(CVSS 9.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-31309) — CVE-2026-31309 공개 (v1.36.0 이후 수정)
