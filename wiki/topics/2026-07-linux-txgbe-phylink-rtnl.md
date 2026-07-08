---
slug: linux-txgbe-phylink-rtnl
first_seen: 2026-07-08
tags: [Linux, 네트워크드라이버, 동시성]
cves: [CVE-2026-46287]
---

Linux txgbe 이더넷 드라이버(구리 NIC와 외부 PHY용)에서 RTNL 뮤텍스 단언(assertion) 위반. 프로브 중 `phylink_connect_phy()` 호출 후 제거 중 `phylink_disconnect_phy()` 호출하면서 RTNL 잠금 요구사항이 불일치. **모듈 제거 시 RTNL 단언 경고** 발생.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46287) — CVE-2026-46287 공개 (CVSS 5.5)

## 관련
