---
slug: prefab-ui-pyodide-rce
first_seen: 2026-11-01
tags: [AI보안, RCE, 샌드박스우회]
cves: [CVE-2026-120338]
---

**Prefab UI**의 생성형 UI 기능이 신뢰할 수 없는 Python 코드를 격리 없이 실행해 원격코드실행 가능하다. Deno 바이너리가 제한 없이 파일시스템과 네트워크에 접근하고 가상환경에 코드를 영구 저장할 수 있다. 0.21.0에서 수정됨.

## 타임라인

- 2026-11-01 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-120338) — CVE-2026-120338 CVSS 10.0 Pyodide 샌드박스 아키텍처 결함 Deno API 노출 공개 (0.21.0 패치)

## 관련

[[wasmtime-sandbox-escape]]
