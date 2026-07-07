---
slug: linux-vfs-unlock
first_seen: 2026-07-07
tags: [Linux kernel, VFS, NFS, locking]
cves: [CVE-2026-53244]
---

Linux 커널 VFS의 nfsd4_create_file() 함수에서 발생하는 잠금 해제 실패 취약점. atomic_create()가 오류 반환 시 dentry 참조를 해제하는 동작이 dentry_create()에 도입되어 잠금이 누수될 수 있음.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53244) — CVE-2026-53244 공개 (CVSS 7.5)
