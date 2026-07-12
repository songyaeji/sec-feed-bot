---
slug: linux-rtl8150-uaf
first_seen: 2026-07-10
tags: [USB드라이버, 사용후해제, 네트워크]
cves: [CVE-2026-52982]
---

Linux 커널 USB RTL8150 드라이버 `rtl8150_start_xmit()` 함수의 사용 후 해제(use-after-free). URB 제출 후 skb->len 접근 시점에 완료 핸들러가 이미 skb을 해제할 수 있음. 멀티코어에서 발생 가능. (CVSS 9.8)

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52982) — Linux RTL8150 패치 공개

## 관련
