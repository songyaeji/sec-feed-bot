---
slug: linux-xfrm-policy-uaf
first_seen: 2026-07-08
tags: [Linux, 커널, 네트워킹]
cves: [CVE-2026-53239]
---

Linux 커널의 **xfrm**(IPSec 암호화 정책) 모듈에서 경합 상태로 인한 해제 후 사용 취약점이 해결됐다. xfrm_policy_bysel_ctx() 함수의 부정확한 bin(버킷) 정리가 원인이다(CVSS 7.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53239) — CVE-2026-53239 공개

## 관련
