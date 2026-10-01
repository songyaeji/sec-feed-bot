---
slug: citrix-netscaler-sept2026-zerodaya
first_seen: 2026-09-26
tags: [RCE, 제로데이, 실제악용중, CISA공식]
cves: [CVE-2026-88771, CVE-2026-88772, CVE-2026-88773, CVE-2026-88774, CVE-2026-88775, CVE-2026-88776, CVE-2026-88777, CVE-2026-88778]
---

**Citrix NetScaler ADC**와 **Citrix NetScaler Gateway**에 패치 전 8개의 치명적 원격코드 실행 취약점이 실제 악용 중이다. CVE-2026-88771·88772는 미인증 RCE를 독립적으로 가능하게 하며 CISA가 KEV 카탈로그에 등록했다.

## 타임라인

- 2026-09-27 [CISA](https://www.cisa.gov/news-events/alerts/2026/09/27/critical-zero-day-vulnerabilities-exploited-citrix-netscaler-adc-gateway) — 8개 CVE 공개, 실제 악용 확인 긴급 알림
- 2026-09-27 [CISA](https://www.cisa.gov/news-events/alerts/2026/09/27/cisa-adds-two-known-exploited-vulnerabilities-catalog) — CVE-2026-88771·88772 KEV 카탈로그 등록
- 2026-09-28 [BleepingComputer](https://www.bleepingcomputer.com/news/security/cisa-orders-feds-to-patch-exploited-citrix-flaws-by-wednesday/) — CISA, 연방 기관에 수요일까지 긴급 패치 명령
- 2026-09-30 [The Hacker News](https://thehackernews.com/2026/09/attackers-exploit-netscaler-flaw-for.html) — Mandiant·Google GTIG 관찰 미확인 공격 그룹의 악용, WHIPSHOT·SLAPSHOT 도구 배포, 북미·유럽 타겟 정부·금융·기술·교육·법률전문가 조직
- 2026-10-01 [The Hacker News](https://thehackernews.com/2026/10/citrix-netscaler-post-exploitation.html) — LevelBlue THOR 팀 분석 post-exploitation 기법 상세, 웹셸 배포·CSS 유사 URL 은폐·설정 정보 탈취 다중 고객 환경 악용 패턴

## 관련

[[citrix-netscaler-auth-bypass]] [[citrix-netscaler-rce-active-exploit]]
