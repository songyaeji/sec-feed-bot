---
slug: linux-kernel-tls-receive-improper-check
first_seen: 2026-09-18
tags: [Linux Kernel, TLS, 암호화통신, CVE-2025-39682]
cves: [CVE-2025-39682]
---

Linux Kernel TLS 수신 경로에서 0바이트 레코드 검색 시 의도된 레코드 타입 처리를 우회하는 취약점이 발견됐다. 암호화된 통신의 무결성 검증 실패로 이어질 수 있으며, 후속 TLS 레코드 처리 오류를 야기할 수 있다.

## 타임라인

- 2026-09-18 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2025-39682) — CVE-2025-39682 공개, TLS rx_list zero-length record 우회

## 관련
