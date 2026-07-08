---
slug: linux-mailbox-probe
first_seen: 2026-07-08
tags: [Linux kernel, 메일박스 드라이버, 자원 누수]
cves: [CVE-2026-53296]
---

Linux 커널 mailbox-test 드라이버의 프로브(probe) 오류 경로에서 발생하는 자원 누수 및 해제 후 사용. 프로브 실패 시 이미 획득한 채널들을 해제하지 않아 메모리 누수 발생. 또한 클라이언트 구조체는 제거되지만 채널은 여전히 활성 상태로 남아 해제 후 사용 시나리오 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53296) — CVE-2026-53296 공개 (CVSS 7.8)
