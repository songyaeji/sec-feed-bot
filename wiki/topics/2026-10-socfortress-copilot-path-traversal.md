---
slug: socfortress-copilot-path-traversal
first_seen: 2026-10-30
tags: [경로조작, 파일쓰기, 보안운영플랫폼]
cves: [CVE-2026-61738]
---

SOCFortress CoPilot의 GCP 보고서 생성 API에서 업로드된 파일명을 검증하지 않아 경로 조작으로 의도한 저장소 밖의 파일을 덮어쓸 수 있는 취약점이다.

## 타임라인

- 2026-10-30 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-61738) — POST /api/scoutsuite/generate-gcp-report 엔드포인트에서 파일명 sanitization 미흡으로 경로 관통 가능, 0.1.77 버전 이상에서 패치

## 관련

[[socfortress-copilot-stored-xss]]
