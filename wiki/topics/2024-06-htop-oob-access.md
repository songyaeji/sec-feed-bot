---
slug: htop-oob-access
first_seen: 2024-06-20
tags: [메모리, 유틸리티, 범위초과]
cves: [CVE-2024-37676]
---

# htop 시스템 모니터링 도구 범위 초과 메모리 접근

시스템 프로세스 모니터 htop v2.20에서 발견된 메모리 안전 취약점. **Header_populateFromSettings** 함수의 범위 초과 접근(Out-of-Bounds, OOB)으로 로컬 정보 유출 또는 DoS 가능(CVSS 8.4).

## 타임라인

- 2024-06-20 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-37676) — CVE-2024-37676: htop v2.20 Header_populateFromSettings 범위 초과 접근
