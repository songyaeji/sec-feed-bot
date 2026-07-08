---
slug: linux-kvec-extract-length
first_seen: 2026-07-08
tags: [Linux, 반복기, 메모리 안전]
cves: [CVE-2026-46289]
---

Linux 커널 라이브러리의 `extract_iter_to_sg()` 함수 kvec 및 user 변형에서 길이 계산 버그. 커널 벡터(kvec) 또는 사용자 공간 반복기(user iterator)에서 scatterlist로 추출할 때 **길이 계산이 오류**나면서 **범위 초과 접근** 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46289) — CVE-2026-46289 공개 (CVSS 9.8)

## 관련
