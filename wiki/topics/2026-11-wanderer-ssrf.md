---
slug: wanderer-ssrf
first_seen: 2026-11-06
tags: [SSRF, 내부서비스, 클라우드메타데이터]
cves: [CVE-2026-71495]
---

**Wanderer** 0.20.0 이전 버전의 `POST /api/v1/trail/download` 핸들러가 공격자 제어 JSON url 필드를 직접 fetch()에 전달해서 **내부 서비스(db:8090, search:7700), 클라우드 메타데이터 주소, 기타 네트워크 대상에 임의 요청** 가능하고 **민감 정보 노출 및 서비스 거부** 위험.

## 타임라인

- 2026-11-06 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-71495) — CVE-2026-71495 공개 (CVSS 10.0, v0.20.0에서 패치)

## 관련
