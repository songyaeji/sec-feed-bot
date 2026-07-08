---
slug: lucene-net-xxe-vuln
first_seen: 2026-07-08
tags: [XML, XXE, .NET라이브러리]
cves: [CVE-2026-47898]
---

**Apache Lucene.Net** 분석 라이브러리(Analysis.Common 4.8.0-beta00005 ~ beta00017)의 XML 파서에서 **XXE(XML External Entity)** 공격 필터링 부재. XML 문서 처리 시 외부 엔티티 참조를 검증하지 않으면서 **서비스 거부(DoS)** 또는 **민감 정보 유출**(로컬 파일 읽기) 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-47898) — CVE-2026-47898 공개 (CVSS 9.8)

## 관련
