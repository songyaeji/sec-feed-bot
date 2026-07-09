---
slug: linux-mac80211-dfs-uaf
first_seen: 2026-05-28
tags: [Linux, WiFi, mac80211, 해제후사용, 드라이버]
cves: [CVE-2026-46166]
---

# Linux WiFi mac80211 DFS CAC 해제 후 사용 취약점

Linux 커널의 **wifi: mac80211** 모듈 DFS(Dynamic Frequency Selection) 처리에서 ieee80211_dfs_cac_cancel 호출이 반복되는 chanctx를 해제 및 제거할 수 있어 slab-use-after-free 오류 가능. **CVSS 8.8**.

## 타임라인

- 2026-05-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46166) — CVE-2026-46166 공개 (CVSS 8.8)
