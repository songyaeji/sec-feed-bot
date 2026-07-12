---
slug: linux-ocfs2-dlm-bounds
first_seen: 2026-07-10
tags: [커널버그, 범위초과, OCFS2]
cves: [CVE-2026-53043]
---

Linux 커널 OCFS2 파일시스템 DLM(Distributed Lock Manager)의 `dlm_match_regions()` 함수 범위 초과 취약점. DLM_QUERY_REGION 네트워크 메시지의 qr_numregions 필드가 O2NM_MAX_REGIONS(32) 검증 부재. 손상된 메시지로 qr_numregions를 255까지 설정 가능하여 qr_regions 버퍼(1024바이트) 범위 초과 읽음. (CVSS 9.1)

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53043) — Linux OCFS2 DLM 패치 공개

## 관련
