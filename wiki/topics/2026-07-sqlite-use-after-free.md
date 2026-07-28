---
slug: sqlite-use-after-free
first_seen: 2026-07-27
tags: [SQLite, 데이터베이스, 사용후해제, DoS]
cves: [CVE-2026-51302]
---

**SQLite 3.41**의 expression 평가 로직의 **사용 후 해제(use-after-free) 취약점**. `sqlite3ReleaseTempReg` 함수가 임시 레지스터 리소스를 부적절히 해제하고 `exprComputeOperands` 함수가 이미 해제된 메모리에 계속 접근. 악의적 SQL 문으로 **서비스 거부, 정보 유출, 임의 코드 실행** 가능. CVSS 9.8.

## 타임라인

- 2026-07-27 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-51302) — CVE-2026-51302 공개 (CVSS 9.8, SQLite 3.41 사용 후 해제)

## 관련

- [[sqlite-vulnerabilities]]
