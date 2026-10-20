---
slug: moxa-aig302-information-disclosure
first_seen: 2026-10-20
tags: [ICS, 암호화키유출, 엣지컴퓨팅]
cves: [CVE-2026-109813]
---

**Moxa AIG-302 ThingsPro Edge** 기기에서 **정보 노출 및 하드코딩된 암호화 키** 취약점이 발견되었다. CVE-2026-109813(CVSS v3.1: 6.8 MEDIUM, CVSS v4.0: 6.9 MEDIUM)로 추적되며, `/usr/bin/sysman` 바이너리의 노출된 개인키 자료를 악용하면 인접한 네트워크 접근으로 기밀성 침해가 가능하다. 패치 v1.4.1이 이용 가능하다.

## 타임라인

- 2026-10-20 [CISA](https://www.cisa.gov/news-events/ics-advisories/icsa-26-293-03) — CISA-26-293-03: Moxa AIG-302 정보 노출, CVE-2026-109813, 패치 v1.4.1 제공

## 관련
