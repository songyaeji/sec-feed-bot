---
slug: linux-netfilter-nft-ct-expect
first_seen: 2026-06-24
tags: [netfilter, 참조누수, 네트워크]
cves: [CVE-2026-52970]
---

Linux netfilter nft_ct expect 오브젝트 평가 코드에서 기대값(expectation) 참조를 해제하지 않는 메모리 누수 발생. nft_ct_expect_obj_eval()이 nf_ct_expect_related() 호출 후 로컬 참조를 반환 전 nf_ct_expect_put()으로 정리하지 않음.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52970) — netfilter nft_ct expect 참조 카운트 누수 공개

## 관련
