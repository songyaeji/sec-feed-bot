---
slug: linux-hugepages-parse
first_seen: 2026-07-08
tags: [커널, 부팅, 널포인터]
cves: [CVE-2026-46284]
---

Linux 커널의 **hugepages/hugepagesz/default_hugepagesz** 커맨드라인 파라미터가 `=` 구분자 없이 지정되면 early_param 파싱이 NULL을 `hugetlb_default_setup()`에 전달하여 널 포인터 역참조를 발생시키는 취약점. 부팅 초기 단계에서 커널 크래시가 가능하다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46284) — CVE-2026-46284 공개 (CVSS 5.5)
