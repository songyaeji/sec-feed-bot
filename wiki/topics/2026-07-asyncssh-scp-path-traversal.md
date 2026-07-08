---
slug: asyncssh-scp-path-traversal
first_seen: 2026-07-08
tags: [경로순회, SSH]
cves: [CVE-2026-54591]
---

**AsyncSSH** Python 라이브러리 2.23.1 이전 버전의 SCP 클라이언트가 악의적 SSH 서버로부터 받은 파일명에 `../` 트래버설을 충분히 검증하지 않아, 공격자가 클라이언트의 파일시스템에 임의 경로로 파일을 쓸 수 있는 취약점. 2.23.1 이상에서 수정됐다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54591) — CVE-2026-54591 공개 (CVSS 8.1)
