---
slug: dpkg-deb-temp-perms
first_seen: 2026-07-08
tags: [vulnerability, debian, temporary-file]
cves: [CVE-2025-6297]
---

dpkg-deb의 임시 디렉터리 권한 검증 결함 **CVE-2025-6297** (CVSS 8.2). 신뢰할 수 없는 데이터 추출 시에도 안전한 작업으로 문서화되어 있으나, 제어 멤버 추출 시 디렉터리 권한을 제대로 검증하지 않아 정리 시 임시 파일이 남을 수 있음.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-6297) — CVE 공개

## 관련

