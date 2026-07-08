---
slug: linux-mailbox-channel-free
first_seen: 2026-07-08
tags: [Linux kernel, 메일박스 드라이버, 이중 해제]
cves: [CVE-2026-53294]
---

Linux 커널 mailbox-test 드라이버의 채널 해제 오류. RX 채널이 다른 MMIO 주소를 가진 TX 채널로 별칭 지정될 때, 채널 정리 중 이 특수 경우를 처리하지 않아 이중 해제(double-free) 발생 가능. mailbox 컨트롤러의 특정 구성에서 메모리 손상 위협.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53294) — CVE-2026-53294 공개 (CVSS 7.8)
