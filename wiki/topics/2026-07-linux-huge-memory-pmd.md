---
slug: linux-huge-memory-pmd
first_seen: 2026-07-07
tags: [Linux kernel, memory management]
cves: [CVE-2026-53155]
---

Linux 커널 huge_memory 모듈의 디바이스 개인 PMD(Page Middle Directory) 엔트리 플래그 설정 오류. 메모리 마이그레이션 기능에서 pmdp_huge_get_and_clear() 사용 시 잘못된 플래그를 설정해 페이지 테이블 관리 오류 발생.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53155) — CVE-2026-53155 공개 (CVSS 5.5)
