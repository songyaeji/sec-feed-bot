---
slug: nats-parser-bypass
first_seen: 2026-07-08
tags: [메시징, 인증우회]
cves: [CVE-2026-58253]
---

**NATS Server** 2.14.0/2.12.7/2.11.16 이전 버전에서 `no_auth_user` 설정 시 보통 클라이언트 연결용 고속 파서가 라우트/리프노드 리스너에도 적용되어, 인증되지 않은 공격자가 내부 통신에 접근 가능한 취약점. 2.14.0 이상에서 수정됐다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-58253) — CVE-2026-58253 공개 (CVSS 8.8)
