---
slug: fluent-forms-cloud-storage-rce
first_seen: 2026-11-14
tags: [WordPress플러그인, 임의파일쓰기, 원격코드실행, 경로순회]
cves: [CVE-2026-120522]
---

# Fluent Forms Cloud Storage Manager — 파일 쓰기 RCE

WordPress 플러그인 **Cloud Storage Manager** (Google Drive/Dropbox/OneDrive/S3 업로드) 1.2.0 이하에서 REST API 미인증 및 경로 검증 누락(CVSS 9.8). 미인증 공격자가 Google Drive 자격증명을 저장한 후 경로 순회를 포함한 파일명으로 공격자 파일을 다운로드하면, basename() 및 sanitize_file_name() 없이 경로 보간되어 웹 접근 디렉터리에 PHP 등 임의 파일을 쓸 수 있어 원격 코드 실행 가능.

## 타임라인

- 2026-11-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-120522) — CVE-2026-120522 REST API 미인증·경로 순회 CVSS 9.8 RCE
