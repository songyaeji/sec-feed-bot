---
slug: linux-zone-device-folio
first_seen: 2026-07-08
tags: [Linux, 커널, 메모리안전]
cves: [CVE-2026-46277]
---

Linux 커널 **zone_device** 메모리 관리에서 `->folio_free()` 콜백 이후 디바이스 **포일리오**(페이지 캐시 관리 단위)를 재접근. 드라이버가 다른 크기로 재할당했을 때 메모리 상태 불일치.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46277) — CVE-2026-46277: zone_device 포일리오 (CVSS 7.8)

## 관련
