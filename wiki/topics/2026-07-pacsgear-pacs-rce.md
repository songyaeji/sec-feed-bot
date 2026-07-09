---
slug: pacsgear-pacs-rce
first_seen: 2026-07-01
tags: [RCE, 의료기기, DICOM, .NET원격처리, 무인증]
cves: [CVE-2026-58126]
---

# PACSgear PACS Scan 의료 영상 관리 시스템 원격코드실행

의료 영상 저장 및 전송 시스템 PACSgear PACS Scan v5.2.1에서 발견된 중대 취약점. 노출된 **.NET Remoting TCP 서비스**(포트 22222, **PGImageExchQueue.exe**)가 인증 검증 없이 임의 파일 읽기/쓰기, 원격 명령 실행 가능(CVSS 9.8).

## 타임라인

- 2026-07-01 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-58126) — CVE-2026-58126: PACSgear PACS Scan v5.2.1 port 22222 .NET Remoting 미인증 RCE
