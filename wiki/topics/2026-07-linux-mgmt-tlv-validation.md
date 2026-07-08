---
slug: linux-mgmt-tlv-validation
first_seen: 2026-07-08
tags: [Linux, Bluetooth, 유효성검증]
cves: [CVE-2026-53255]
---

Linux 커널 Bluetooth MGMT 계층의 광고 데이터 TLV(Type-Length-Value) 검증 순서 오류. `tlv_data_is_valid()` 함수가 각 필드의 길이를 data[i]에서 읽은 후 data[i + 1]을 검사하여 관리형 EIR 타입 확인하지만, 현재 필드가 여전히 경계 내에 있는지 먼저 확인하지 않음. 잘못된 광고 데이터 처리 시 **범위 초과 접근** 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53255) — CVE-2026-53255 공개 (CVSS 7.1)

## 관련
