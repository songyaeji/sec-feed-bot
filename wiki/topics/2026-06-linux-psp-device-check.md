---
slug: linux-psp-device-check
first_seen: 2026-06-24
tags: [네트워킹, 장치관리, 참조추적]
cves: [CVE-2026-52979]
---

Linux PSP 드라이버의 psp_assoc_device_get_locked()에서 장치 등록 해제 시 경합 조건 발생. RCU 참조 획득 후 락 획득 사이에 psp_dev_unregister()가 완료되고 상태를 초기화하지만, 락 이후 장치 생존 여부 확인 누락. psp_dev_is_registered() 함수 존재하지만 미사용.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52979) — psp device unregister 검사 누락 공개

## 관련
[[linux-psp-permission-check]]
