---
slug: umbraco-file-upload-rce
first_seen: 2025-12-22
tags: [CMS, 파일업로드, RCE]
cves: [CVE-2025-67288, CVE-2023-49279]
---

Umbraco CMS v16.3.3에서 임의 파일 업로드 취약점이 발견됐다. 공격자가 조작된 PDF 파일을 업로드해 임의코드 실행이 가능하다. 공급사는 파일 검증 책임이 시스템 관리자에게 있다고 주장하고 있으며, PDF JavaScript는 완전히 격리된 샌드박스 내에서 실행된다고 해명했다. CVSS 10.0으로 평가된다.

## 타임라인

- 2025-12-22 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-67288) — CVE-2025-67288 Umbraco CMS v16.3.3 PDF 파일 업로드 임의코드 실행 CVSS 10.0 (공급사 이의 제기)

## 관련

