---
slug: linux-ksmbd-fsctl-permission
first_seen: 2026-07-07
tags: [Linux kernel, privilege escalation, file server]
cves: [CVE-2026-52944]
---

Linux 커널 ksmbd(SMB 파일서버 구현)의 FSCTL_SET_SPARSE 명령에서 권한 검증 부재. 파일의 스파스 속성을 수정하고 xattr로 저장할 때 표준 사용자도 접근 가능해 권한상향 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52944) — CVE-2026-52944 공개 (CVSS N/A)
