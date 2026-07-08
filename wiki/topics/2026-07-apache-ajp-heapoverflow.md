---
slug: apache-ajp-heapoverflow
first_seen: 2026-07-08
tags: [Apache, 웹서버, Tomcat]
cves: [CVE-2026-28780]
---

Apache HTTP Server의 **mod_proxy_ajp** 모듈이 악의적 AJP 서버로부터 메시지를 받을 때, 공격자가 제어하는 4바이트를 힙 버퍼 끝 너머에 쓸 수 있다(CVSS 9.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-28780) — CVE-2026-28780 공개

## 관련
