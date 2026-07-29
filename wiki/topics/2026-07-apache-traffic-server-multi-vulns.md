---
slug: apache-traffic-server-multi-vulns
first_seen: 2026-07-29
tags: [Apache, TrafficServer, RCE, 요청스머글링]
cves: [CVE-2026-33267, CVE-2026-57834, CVE-2026-58150, CVE-2026-58162]
---

Apache Traffic Server 2026-07-29 보안 업데이트에서 4개의 중대 취약점이 공개됐다. 부적절한 입력 검증, 청크 메시지 스머글링, HTTP/2 다운그레이드 공격, 공격자 제어 인증서 생성 등 다양한 공격 벡터를 포함한다. 9.2.15와 10.1.4 버전으로의 즉시 업그레이드가 권장된다.

## 타임라인

- 2026-07-29 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-33267) — CVE-2026-33267: 부적절한 입력 검증 (CVSS 10.0)
- 2026-07-29 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-57834) — CVE-2026-57834: 청크 메시지 요청 스머글링 (CVSS 10.0)
- 2026-07-29 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-58150) — CVE-2026-58150: HTTP/2 Transfer-Encoding 다운그레이드 (CVSS 10.0)
- 2026-07-29 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-58162) — CVE-2026-58162: 인증서 생성 SNI 기반 (CVSS 10.0)
