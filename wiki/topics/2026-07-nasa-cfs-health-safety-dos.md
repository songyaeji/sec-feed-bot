---
slug: nasa-cfs-health-safety-dos
first_seen: 2026-07-16
tags: [우주항공, DoS, CVE-2026-15352]
cves: [CVE-2026-15352]
---

NASA **Core Flight System(cFS)** Health & Safety 애플리케이션에서 NULL 포인터 역참조 취약점(CVE-2026-15352)이 발견되었다. 정기적 Housekeeping Telemetry 요청 처리 중 segmentation fault로 인한 애플리케이션 크래시 및 서비스 거부가 가능하다. 항공우주 임무 제어 시스템의 신뢰성에 영향을 미칠 수 있다.

## 타임라인

- 2026-07-16 [CISA ICS Advisory ICSA-26-197-03](https://www.cisa.gov/news-events/ics-advisories/icsa-26-197-03) — NASA cFS Health & Safety Application NULL 포인터 역참조 DoS 공개
