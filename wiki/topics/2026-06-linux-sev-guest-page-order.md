---
slug: linux-sev-guest-page-order
first_seen: 2026-06-24
tags: [커널버그, SEV, 메모리안전]
cves: [CVE-2026-52959]
---

Linux 커널 arch/x86의 `get_ext_report()` 함수에서 SEV 게스트 확장 리포트 요청 시 메모리 할당 크기 불일치로 인한 페이지 할당자 손상. 호스트가 SNP_GUEST_VMM_ERR_INVALID_LEN 오류로 반환한 certs_len을 정리에 사용하여 원래 할당 페이지 순서와 불일치. alloc_pages_exact 함수 사용으로 정확한 크기 관리하여 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52959) — Linux SEV 게스트 패치 공개

## 관련
