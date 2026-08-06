---
slug: custom-fields-wordpress-delete
first_seen: 2026-08-05
tags: [WordPress, 플러그인, 파일삭제]
cves: [CVE-2026-16940]
---

# WordPress Custom Fields 플러그인 - 미인증 임의 파일 삭제

**CVE-2026-16940** WordPress Custom Fields 플러그인 v1.5.1 이전 버전에서 미인증 사용자가 경로 검증 없이 서버의 임의 파일(wp-config.php 등)을 삭제할 수 있는 취약점. 파일 삭제로 사이트 완전 탈취 가능. **CVSS 10.0** 중대 취약점.

## 타임라인

- 2026-08-05 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16940) — CVE-2026-16940 공개 (CVSS 10.0, 미인증 파일 삭제)
