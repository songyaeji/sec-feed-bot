---
slug: linux-imagination-drm-ftrace
first_seen: 2026-07-08
tags: [Linux, GPU, 디버그]
cves: [CVE-2026-46278]
---

Linux 커널 **imagination drm** 드라이버의 ftrace 마스크 업데이트 시 debugfs 엔트리로 **잘못된 데이터**를 전달해 NULL 포인터 역참조. 커널 크래시로 이어짐.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46278) — CVE-2026-46278: imagination drm ftrace (CVSS 5.5)

## 관련
