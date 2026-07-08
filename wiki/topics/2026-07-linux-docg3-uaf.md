---
slug: linux-docg3-uaf
first_seen: 2026-07-08
tags: [커널, MTD, 해제후사용]
cves: [CVE-2026-46285]
---

Linux 커널의 MTD (Memory Technology Device) **docg3 드라이버**의 `docg3_release()` 함수에서 docg3 포인터를 미리 저장한 후 루프 내에서 `doc_release_device()`로 각 floor를 해제하면서 해제된 메모리에 접근하는 use-after-free 취약점. 메모리 손상 및 권한상향이 가능하다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46285) — CVE-2026-46285 공개 (CVSS 7.8)
