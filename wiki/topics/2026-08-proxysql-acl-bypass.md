---
slug: proxysql-acl-bypass
first_seen: 2026-08-10
tags: [프로토콜우회, 데이터베이스프록시, ACL우회, CVSS10.0]
cves: [CVE-2026-48772]
---

**ProxySQL** 2.0.0~3.0.8에서 HAProxy PROXY 프로토콜 v1을 부정확하게 처리해, 공격자가 클라이언트 주소를 위조하면서 쿼리 라우팅 규칙과 ACL을 우회할 수 있다. `mysql-proxy_protocol_networks = '*'` (기본값)일 때 TCP 접속자는 임의의 출처 IP를 주장할 수 있어 읽기/쓰기 분리, 스키마 격리, 쿼리 필터 규칙을 무효화할 수 있다.

## 타임라인

- 2026-08-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-48772) — ProxySQL 2.0.0~3.0.8 PROXY 프로토콜 주소 스푸핑 ACL 우회 CVSS 10.0 (3.0.9에서 패치)
