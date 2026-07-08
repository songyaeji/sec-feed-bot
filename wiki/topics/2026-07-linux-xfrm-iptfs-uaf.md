---
slug: linux-xfrm-iptfs-uaf
first_seen: 2026-07-08
tags: [Linux, 커널, 터널링]
cves: [CVE-2026-53240]
---

Linux 커널의 **xfrm iptfs**(IPsec 터널 암호화) 모듈에서 패킷 재구성 중 경합 상태로 인한 해제 후 사용 취약점이 발견됐다. __input_process_payload() 함수가 first_skb 포인터를 부정확하게 처리한다(CVSS 8.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53240) — CVE-2026-53240 공개

## 관련
