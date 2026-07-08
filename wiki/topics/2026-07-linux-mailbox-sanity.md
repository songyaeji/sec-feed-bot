---
slug: linux-mailbox-sanity
first_seen: 2026-07-08
tags: [Linux kernel, 메일박스 드라이버, 입력 검증]
cves: [CVE-2026-53295]
---

Linux 커널 mailbox 드라이버의 채널 배열 검증 누락. 메일박스 컨트롤러에 채널 배열이 연결되지 않은 경우 정상적으로 실패 처리하지 않으면 이후 역참조에서 OOPS 발생 가능. 메일박스 컨트롤러 미초기화 상태에서 메모리 접근 오류 야기.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53295) — CVE-2026-53295 공개 (CVSS 5.5)
