---
slug: linux-smb-multichannel-uaf
first_seen: 2025-05-01
tags: [해제후사용, SMB, 다중채널]
cves: [CVE-2025-37750]
---

Linux 커널 CIFS 클라이언트의 SMB 다중채널 복호화에서 각 채널이 주 채널의 AEAD TFM(Transform Module)을 동시에 접근하면서 경쟁 조건으로 인한 메모리 사용 후 해제(Use-After-Free)가 발생한다.

## 타임라인

- 2025-05-01 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-37750) — 채널별 독립 AEAD 인스턴스 할당으로 동시 접근 제거하도록 패치

## 관련

없음
