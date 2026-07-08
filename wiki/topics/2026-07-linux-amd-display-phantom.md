---
slug: linux-amd-display-phantom
first_seen: 2026-07-08
tags: [Linux kernel, 디스플레이 드라이버, 부동소수점 상태]
cves: [CVE-2026-53285]
---

Linux 커널 DRM/AMD 디스플레이 드라이버의 phantom-plane 할당 처리 결함. dcn32_validate_bandwidth()가 dcn32_internal_validate_bw()를 DC_FP_START()/DC_FP_END()로 감싸는데, x86 non-RT 환경에서 부동소수점 레지스터 상태 관리 누락으로 인한 코프로세서 오류 발생 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53285) — CVE-2026-53285 공개 (CVSS 5.5)
