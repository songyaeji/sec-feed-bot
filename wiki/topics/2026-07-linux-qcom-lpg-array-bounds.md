---
slug: linux-qcom-lpg-array-bounds
first_seen: 2026-07-08
tags: [Linux, LED드라이버, 배열경계]
cves: [CVE-2026-46286]
---

Linux Qualcomm LPG(LED PWM Generator) 드라이버에서 고해상도 값 선택 시 배열 경계 검증 누락. `FIELD_GET()`으로 3비트 레지스터에서 값을 추출하지만 인덱싱할 배열은 5개 요소만 보유. **배열 경계 초과** 접근 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46286) — CVE-2026-46286 공개 (CVSS 5.5)

## 관련
