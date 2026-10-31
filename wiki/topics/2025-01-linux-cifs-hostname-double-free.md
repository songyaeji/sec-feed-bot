---
slug: linux-cifs-hostname-double-free
first_seen: 2025-01-31
tags: [이중해제, CIFS, 커널크래시]
cves: [CVE-2025-21673]
---

Linux 커널 CIFS 클라이언트의 cifs_put_tcp_session 함수에서 TCP 연결 셧다운 시 server->hostname을 이중 해제하는 취약점이다. DFS 재연결 중 hostname이 여러 번 참조되므로 cifsd 스레드가 종료될 때까지 해제를 지연해야 한다.

## 타임라인

- 2025-01-31 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-21673) — hostname 해제 시점을 cifsd 스레드 종료 후로 지연하도록 패치

## 관련

없음
