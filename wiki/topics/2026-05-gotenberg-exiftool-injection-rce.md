---
slug: gotenberg-exiftool-injection-rce
first_seen: 2026-05-06
tags: [PDF, 문서변환, 명령인젝션, ExifTool, 원격코드실행]
cves: [CVE-2026-40281]
---

# Gotenberg — ExifTool 메타데이터 인젝션 RCE

Gotenberg Docker 기반 무상태 PDF API 8.30.1 이전 버전에서 메타데이터 쓰기 엔드포인트가 메타데이터 값을 검증하지 않는 취약점이 발견됐다. 메타데이터 값에 개행 문자를 삽입하면 ExifTool stdin 라인이 분리되어 -FileName, -Directory, -SymLink, -HardLink 같은 임의 ExifTool 의사태그를 인젝션할 수 있다. 미인증 공격자가 컨테이너 파일시스템 내 임의 경로로 PDF를 이동·삭제하거나 심링크·하드링크를 생성할 수 있다.

## 타임라인

- 2026-05-06 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-40281) — CVE-2026-40281 공개, CVSS 10.0

## 관련
