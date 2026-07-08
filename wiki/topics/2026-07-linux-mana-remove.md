---
slug: linux-mana-remove
first_seen: 2026-07-08
tags: [Linux kernel, 네트워크 드라이버, 상태 관리]
cves: [CVE-2026-53297]
---

Linux 커널 net/mana 드라이버의 mana_remove() 함수 중복 호출 방어 부족. 절전 모드 복구(PM resume) 중 mana_attach() 실패 시 mana_probe()가 mana_remove()를 호출하는데, 이 함수가 여러 번 호출되어도 gd->gdma_context와 gd->driver_data를 NULL로 설정한 후 이를 검사하지 않아 NULL 역참조 위협.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53297) — CVE-2026-53297 공개 (CVSS 5.5)
