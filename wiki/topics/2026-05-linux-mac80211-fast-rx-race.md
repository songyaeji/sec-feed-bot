---
slug: linux-mac80211-fast-rx-race
first_seen: 2026-05-28
tags: [Linux, WiFi, mac80211, 경합조건, 드라이버]
cves: [CVE-2026-46152]
---

# Linux WiFi mac80211 fast-RX 경합조건 취약점

Linux 커널의 **wifi: mac80211** 모듈에서 ieee80211_invoke_fast_rx() 함수가 병렬 RX에 안전하도록 문서화되었으나 per-invocation rx_result를 static으로 선언하여 동시 호출자가 같은 인스턴스를 공유하는 경합조건. **CVSS 8.8**.

## 타임라인

- 2026-05-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46152) — CVE-2026-46152 공개 (CVSS 8.8)
