---
slug: budibase-webhook-sqli
first_seen: 2026-08-13
tags: [SQL인젝션, 자동화플랫폼, 데이터베이스, CVSS10.0]
cves: [CVE-2026-72851]
---

# Budibase 웹훅 자동화 SQL 인젝션

**Budibase** 3.40.0 이전의 웹훅 자동화 기능에서 EXECUTE_QUERY 스텝이 입력값을 검증하지 않아 **SQL injection** 취약점이 발생했다. 공격자가 웹훅 엔드포인트로 조작된 JSON을 전송하면 빌더가 설정한 데이터베이스 자격증명으로 SQL 명령을 실행해 **Snowflake** 등 연결된 데이터베이스에 대한 데이터 유출·수정·지속성 침입이 가능하다.

## 타임라인

- 2026-08-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-72851) — CVE-2026-72851 Budibase webhook EXECUTE_QUERY SQL injection 공개 (CVSS 10.0)

## 관련
