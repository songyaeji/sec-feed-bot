---
slug: corewcf-namedpipe-interception
first_seen: 2026-07-08
tags: [로컬권한상향, IPC]
cves: [CVE-2026-54777]
---

CoreWCF 1.8.1, 1.9.1 이전 버전의 NetNamedPipe 트랜스포트에서 기존 named pipe 인스턴스에 연결이 가능하며, 공격자가 race condition을 이용해 로컬 시스템의 다른 프로세스 간 통신을 가로챌 수 있다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54777) — CVE-2026-54777 (CVSS 6.5) 공개

## 관련

