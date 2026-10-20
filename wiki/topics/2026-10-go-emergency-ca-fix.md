---
slug: go-emergency-ca-fix
first_seen: 2026-10-20
tags: [CA손상, 인증서거부, 긴급패치]
cves: []
---

Go 프로그래밍 언어가 1.27.3, 1.26.10 긴급 패치로 손상된 8개 intermediate CA 키를 거부하도록 인증서 검증을 강화했다. 해당 키에서 발급된 인증서는 new Go 바이너리에서 거부되어 연쇄 서비스 차단이 우려된다.

## 타임라인

- 2026-10-20 [The Hacker News](https://thehackernews.com/2026/10/go-issues-emergency-update-blocking.html) — **Go 1.27.3·1.26.10** 긴급 패치, 8개 intermediate CA 키에서 발급된 인증서 거부 설정
