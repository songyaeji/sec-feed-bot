---
slug: linux-sctp-chunk-overflow
first_seen: 2026-07-07
tags: [Linux kernel, buffer overflow, SCTP protocol, RCE]
cves: [CVE-2026-53246]
---

Linux 커널 SCTP 프로토콜 리스닝 서버의 버퍼 오버플로우 취약점. COOKIE_ECHO 청크 처리 시 캐시된 피어 INIT 청크 길이를 검증하지 않아 매개변수 파싱 중 버퍼 오버플로우 발생. 네트워크 기반 원격 코드 실행 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53246) — CVE-2026-53246 공개 (CVSS 9.8)
