---
slug: joomla-contact-vcard
first_seen: 2026-07-07
tags: [Joomla, 권한검증우회, 개인정보유출]
cves: [CVE-2026-48948]
---

Joomla의 **com_contact** 모듈에서 접근 제어 검증 부실로 권한이 없는 사용자가 카테고리별 제한 대상 연락처의 vCard 파일을 다운로드할 수 있다. 카테고리 권한 검증을 무시하고 직접 접근이 가능해 개인정보 노출 위험.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-48948) — CVE-2026-48948 (CVSS 8.8) 공개
