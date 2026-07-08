---
slug: dgraph-unauth-snapshot
first_seen: 2026-07-08
tags: [Dgraph, 미인증, RCE]
cves: [CVE-2026-54061]
---

오픈소스 그래프 데이터베이스 **Dgraph** 25.3.5 이전의 Alpha 서버가 외부 스냅샷 import RPC를 공개 gRPC 포트(`:9080`)에 **미인증** 노출. 원격 공격자가 `StreamExtSnapshot`을 통해 임의 코드를 실행할 수 있으며, 데이터 유출 및 시스템 완전 제어 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54061) — CVE-2026-54061: 미인증 스냅샷 임포트 RCE (CVSS 9.1)

## 관련
