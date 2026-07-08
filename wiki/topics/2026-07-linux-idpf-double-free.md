---
slug: linux-idpf-double-free
first_seen: 2026-07-08
tags: [Linux kernel, 네트워크 드라이버, 메모리 안전성, 이중 해제]
cves: [CVE-2026-53286]
---

Linux 커널 idpf 네트워크 드라이버의 보조 장치 에러 경로에서 발생하는 이중 해제(double-free) 및 해제 후 사용(use-after-free) 취약점. auxiliary_device_add() 실패 시 auxiliary_device_uninit() 호출 후 같은 객체에 대해 또 다른 정리 루틴이 실행되어 메모리 손상 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53286) — CVE-2026-53286 공개 (CVSS 7.8)
