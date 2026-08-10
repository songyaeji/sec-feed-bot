---
slug: metabase-sqli-zerodday
first_seen: 2026-08-07
tags: [제로데이, SQLi, 데이터유출사고, BI플랫폼]
cves: []
---

**Metabase** 오픈소스 BI 대시보드 플랫폼에 SQL 인젝션 제로데이 취약점이 존재하며, 미인증 상태로 이미 악용되고 있다. **Framework**와 **Tally** 등 주요 고객사의 인스턴스에서 데이터 탈취 공격이 발생했으며, 양사 모두 침해 사실을 공식 인정했다. 기업 비즈니스 인텔리전스 시스템의 보안 위협이 심각함을 드러냈다.

## 타임라인

- 2026-08-07 [BleepingComputer](https://www.bleepingcomputer.com/news/security/framework-tally-disclose-metabase-data-theft-attacks/) — Metabase SQLi 제로데이 악용 Framework·Tally 데이터 탈취 사건
- 2026-08-10 [NVD CVE-2026-72898](https://nvd.nist.gov/vuln/detail/CVE-2026-72898) — `/reset_password` 데이터베이스 엔드포인트 비인증 SQL 인젝션 CVSS 10.0
- 2026-08-10 [NVD CVE-2026-72899](https://nvd.nist.gov/vuln/detail/CVE-2026-72899) — 공개 공유 카드·대시보드 필드필터 파라미터 비인증 SQL 인젝션 CVSS 10.0
