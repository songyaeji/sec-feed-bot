---
slug: linux-smb-symlink-data-loop
first_seen: 2026-06-24
tags: [커널버그, SMB, 서비스거부]
cves: [CVE-2026-52967]
---

Linux 커널 fs/smb의 `symlink_data()` 함수에서 ErrorDataLength 범위 검증 부재로 인한 무한 루프 및 범위 초과 메모리 접근. 32비트 아키텍처에서 ErrorDataLength == 0xfffffff8일 때 다음 포인터가 현재 포인터와 같아져 무한 루프, 또는 0xfffffff0일 때 범위 이전 메모리 접근. SMB 클라이언트가 손상된 SMB 응답 처리 시 서비스 거부 또는 정보 유출 가능.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52967) — Linux smb/client 패치 공개

## 관련
