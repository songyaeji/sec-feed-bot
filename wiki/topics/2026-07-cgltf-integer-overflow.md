---
slug: cgltf-integer-overflow
first_seen: 2026-07-07
tags: [parsing, integer overflow, graphics]
cves: [CVE-2026-32845]
---

cgltf glTF 파서 라이브러리의 정수 오버플로우 취약점. cgltf_validate() 함수에서 스파스 접근자 검증 시 size 계산에서 정수 오버플로우 발생. 악의적 glTF/GLB 파일로 범위 외 메모리 읽기 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-32845) — CVE-2026-32845 공개 (CVSS 8.4)
