---
slug: linux-audit-capset
first_seen: 2026-07-08
tags: [Linux kernel, 감시, 권한 관리]
cves: [CVE-2026-53287]
---

Linux 커널 audit 서브시스템의 CAPSET 레코드 생성 오류. __audit_log_capset()에서 복사-붙여넣기 실수로 유효한 권한(effective capability) 집합을 상속 가능 권한(inheritable) 필드에 기록하여 모든 CAPSET 감시 레코드가 잘못된 권한 정보를 보고하는 문제.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53287) — CVE-2026-53287 공개 (CVSS 5.5)
