---
slug: linux-af-alg-race-condition
first_seen: 2026-09-18
tags: [경쟁조건, Linux커널, 암호화API]
cves: [CVE-2025-39964]
---

**Linux Kernel** AF_ALG 소켓에 대한 동시 쓰기 시 데이터가 예측 불가능하게 섞이고 소켓 내부 상태가 불일치되는 경쟁 조건 취약점이 발견됐다. **libsodium** 등 암호화 관련 사용자 공간 라이브러리에서 AF_ALG 인터페이스를 사용하는 프로그램에 영향을 미칠 수 있다.

## 타임라인

- 2026-09-18 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2025-39964) — CVE-2025-39964 Linux Kernel AF_ALG 소켓 경쟁 조건 CISA KEV 게재

## 관련
