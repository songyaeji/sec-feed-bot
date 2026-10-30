---
slug: wasmtime-sandbox-escape
first_seen: 2026-10-23
tags: [WebAssembly, 샌드박스이스케이프, CVE-2026-115893]
cves: [CVE-2026-115893]
---

WebAssembly 런타임 Wasmtime의 Cranelift 컴파일러 aarch64 분기 조건 버그로 사용자 제어 Wasm 모듈이 샌드박스를 탈출할 수 있음. 에지·컨테이너 보안 침해.

## 타임라인

- 2026-10-23 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-115893) — CVE-2026-115893 CVSS 9.9 샌드박스 이스케이프 36.0.19, 48.0.7, 49.0.4 이상에서 수정

## 관련
