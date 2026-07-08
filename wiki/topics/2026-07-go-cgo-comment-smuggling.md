---
slug: go-cgo-comment-smuggling
first_seen: 2026-07-08
tags: [Go, 공급망, 컴파일]
cves: [CVE-2025-61732]
---

Go **cgo**(C 상호작용 기능)에서 Go와 C/C++ 주석 형식의 파싱 차이를 악용한 코드 스머글링 취약점이 발견됐다. C 섹션에 숨겨진 코드가 소스 검토 시에는 감지되지 않다가 컴파일 단계에서 최종 바이너리에 포함된다(CVSS 8.6).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-61732) — CVE-2025-61732 공개

## 관련
