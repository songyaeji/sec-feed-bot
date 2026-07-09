---
slug: swig-cgo-code-smuggling
first_seen: 2026-04-08
tags: [SWIG, 빌드, CGO, 코드스머글링]
cves: [CVE-2026-27140]
---

# SWIG 파일명 CGO 코드 스머글링 취약점

**SWIG** (Simplified Wrapper and Interface Generator) 파일명에 'cgo'를 포함하고 정교한 payload를 조합했을 때 신뢰 계층 우회를 통한 코드 스머글링 및 빌드 시간 임의 코드 실행이 가능. **CVSS 8.8** 빌드타임 취약점.

## 타임라인

- 2026-04-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-27140) — CVE-2026-27140 공개 (CVSS 8.8)
