---
slug: link-library-wordpress-file-deletion
first_seen: 2026-08-15
tags: [WordPress, 파일삭제, 플러그인, 경로검증우회]
cves: [CVE-2026-18855]
---

Link Library WordPress 플러그인 7.9.4 이하에서 ll_delete_link_fields 함수의 파일 경로 검증이 불충분하여, '링크 삭제 시 로컬 파일 삭제' 옵션이 활성화된 경우 관리자가 공격자 제출 링크를 영구 삭제 시 wp-config.php 같은 임의 파일 삭제 및 원격코드 실행 가능. 공격 표면 제한(관리자의 수동 삭제 조치 필요). CVSS 9.1.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-18855) — CVE-2026-18855 공개, 경로검증 우회로 인한 조건부 파일 삭제 취약점 확인
