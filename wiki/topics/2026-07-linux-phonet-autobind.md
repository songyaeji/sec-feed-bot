---
slug: linux-phonet-autobind
first_seen: 2026-07-08
tags: [Linux kernel, 네트워크 프로토콜]
cves: [CVE-2026-53292]
---

Linux 커널 phonet 프로토콜 스택의 pn_socket_autobind() 함수에서 발생하는 BUG_ON() 호출. 자동 바인드 실패 시 커널 panic을 유발하여, 악의적인 사용자 또는 오동작하는 애플리케이션이 DoS 공격에 사용 가능. syzbot이 pn_socket_sendmsg() 경로를 통한 트리거 확인.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53292) — CVE-2026-53292 공개 (CVSS 5.5)
