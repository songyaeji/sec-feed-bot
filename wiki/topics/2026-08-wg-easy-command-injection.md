---
slug: wg-easy-command-injection
first_seen: 2026-08-11
tags: [WireGuard, VPN, 명령주입]
cves: [CVE-2026-72603]
---

**wg-easy** 15.3.0 버전에서 클라이언트명 입력값 검증이 부족해, `clients.create` 권한 보유자가 개행 문자를 주입해 WireGuard PostUp 지시문을 악용하고 루트 권한으로 코드를 실행할 수 있다. CVSS 9.9의 중대 취약점이다.

## 타임라인

- 2026-08-11 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-72603) — CVE-2026-72603 공개 (CVSS 9.9, 클라이언트명 명령 주입)
