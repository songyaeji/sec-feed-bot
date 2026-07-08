---
slug: linux-iowq-hash-tail
first_seen: 2026-07-08
tags: [Linux, 커널, 메모리안전]
cves: [CVE-2026-46274]
---

Linux 커널 **io-wq** I/O 작업 큐에서 `io_wq_remove_pending()`이 취소된 작업이 해시 버킷의 **테일**일 때 테일 포인터 검증을 누락. 해시 버킷 손상으로 인한 DoS 또는 메모리 오염.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46274) — CVE-2026-46274: io-wq 해시 테일 검증 (CVSS 7.8)

## 관련
