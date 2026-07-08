---
slug: onnx-upsample-null-deref
first_seen: 2026-07-08
tags: [AI, 머신러닝, 서비스거부]
cves: [CVE-2026-44512]
---

**ONNX** (Open Neural Network Exchange) 1.9.0~1.22.0 버전에서 `Upsample_6_7::adapt_upsample_6_7()` 함수가 특정 입력 처리 시 널 포인터를 역참조하여 서비스거부를 발생시키는 취약점. 1.22.0 이상에서 수정됐다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44512) — CVE-2026-44512 공개 (CVSS 5.5)
