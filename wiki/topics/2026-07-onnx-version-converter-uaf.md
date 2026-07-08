---
slug: onnx-version-converter-uaf
first_seen: 2026-07-08
tags: [AI]
cves: [CVE-2026-44512]
---

**ONNX** (Open Neural Network Exchange) 1.22.0 이전의 버전 컨버터가 Upsample 연산 처리 중 NULL 포인터를 역참조하여 프로세스 크래시를 일으킨다. 특정 형식의 모델 파일을 처리할 때 발생하는 메모리 안전 결함.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44512) — CVE-2026-44512 공개 (CVSS 5.5)
