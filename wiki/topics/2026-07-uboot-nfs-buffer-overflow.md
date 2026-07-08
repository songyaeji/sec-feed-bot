---
slug: uboot-nfs-buffer-overflow
first_seen: 2026-07-08
tags: [부트로더, NFS, 메모리 안전]
cves: [CVE-2026-29009]
---

U-Boot 2026.04-rc3 이전의 NFS 클라이언트에서 `nfs_readlink_reply()` 함수의 버퍼 오버플로우. CONFIG_CMD_NFS 활성화 시 2048바이트 `nfs_path_buff` 버퍼에 NFS 서버 응답의 상대 심링크(symlink) 목표를 제한 없이 누적 기록. 악의적이거나 손상된 NFS 서버가 여러 상대 심링크 대상을 반환하면 **스택 버퍼 오버플로우** 발생으로 코드 실행 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-29009) — CVE-2026-29009 공개 (CVSS 8.2)

## 관련
