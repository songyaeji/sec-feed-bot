---
slug: linux-xe-eustall-resource
first_seen: 2026-07-08
tags: [Linux kernel, 그래픽 드라이버, 자원 정리, RCE]
cves: [CVE-2026-53290]
---

Linux 커널 drm/xe 그래픽 드라이버의 EU stall 스트림 정리 오류. xe_eu_stall_stream_close()에서 스트림 비활성화 및 자원 해제 전에 drm_dev_put()을 호출하여, 이것이 마지막 참조를 제거할 경우 이후 접근에서 해제된 장치 메모리 접근 가능. 권한 코드 실행 위협.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53290) — CVE-2026-53290 공개 (CVSS 7.8)
