---
slug: koollab-lms-scorm-upload-rce
first_seen: 2026-07-29
tags: [Koollab, LMS, SCORM, 파일업로드, RCE]
cves: [CVE-2026-63227]
---

Koollab LMS에서 SCORM 파일 업로드 제한이 없어 인증된 모듈 디자이너가 PHP 웹셸을 포함한 SCORM 패키지를 공개 접근 가능 디렉터리에 업로드해 임의 코드를 실행할 수 있다.

## 타임라인

- 2026-07-29 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-63227) — CVE-2026-63227 공개, SCORM 파일 업로드 RCE (CVSS 9.9)
