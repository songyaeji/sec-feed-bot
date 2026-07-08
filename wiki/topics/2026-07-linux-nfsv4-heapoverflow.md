---
slug: linux-nfsv4-heapoverflow
first_seen: 2026-07-08
tags: [Linux, 커널, NFS]
cves: [CVE-2026-31402]
---

Linux 커널의 **nfsd**(NFS 데몬) NFSv4.0 구현에서 재생 캐시 용도의 고정 크기 버퍼(rp_ibuf[112바이트])로 큰 응답을 처리할 때 힙 오버플로우 취약점이 발생한다(CVSS 9.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-31402) — CVE-2026-31402 공개

## 관련
