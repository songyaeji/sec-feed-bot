---
slug: linux-ena-phc-uaf
first_seen: 2026-06-24
tags: [네트워크드라이버, 사용후해제, 동시성]
cves: [CVE-2026-52971]
---

AWS ENA(Elastic Network Adapter) 드라이버의 PHC(Precision Hardware Clock) get_timestamp 경로에서 스핀락 전에 phc->active를 확인해 시간초과 취약성 발생. ena_com_phc_destroy() 실행 중 메모리 해제 후 NULL 포인터 역참조 가능. 스핀락 내에서 모든 상태 및 포인터 확인 필요.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52971) — ENA PHC 사용 후 해제 취약점 공개

## 관련
