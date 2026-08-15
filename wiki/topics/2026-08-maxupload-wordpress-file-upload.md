---
slug: maxupload-wordpress-file-upload
first_seen: 2026-08-15
tags: [WordPress, 파일업로드, 플러그인, 검증우회]
cves: [CVE-2026-15965]
---

MaxUpload – Big File Uploads – Increase Maximum File Upload Size WordPress 플러그인 1.4.0 이하에서 handle_upload 함수의 파일명 검증이 중간 청크 파일명만 수행하고 최종 조합 파일명(resumableFilename 파라미터)은 검증하지 않아, 미인증 사용자가 실행 가능한 파일 확장자로 업로드 및 원격코드 실행 가능. CVSS 8.8.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15965) — CVE-2026-15965 공개, 파일명 검증 우회로 인한 임의 파일 업로드 취약점 확인
