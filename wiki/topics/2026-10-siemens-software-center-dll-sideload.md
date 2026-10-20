---
slug: siemens-software-center-dll-sideload
first_seen: 2026-10-20
tags: [취약점악용, ClickFix, DLL사이드로딩]
cves: [CVE-2026-110936]
---

**Siemens Software Center**의 DLL 사이드로딩 취약점(CVE-2026-110936, CVSS 8.4)이 **ClickFix** 캠페인에 의해 적극 악용되고 있다. 애플리케이션이 검색하는 디렉터리에 악의적 DLL을 배치하여 메모리에 로드되는 시점의 권한으로 악성코드를 실행할 수 있다.

## 타임라인

- 2026-10-20 [The Hacker News](https://thehackernews.com/2026/10/clickfix-attackers-exploit-siemens.html) — Siemens, Siemens Software Center DLL 사이드로딩 취약점(CVE-2026-110936) 패치, ClickFix 공격에서 실제 악용 확인

## 관련

[[clickfix-google-visualization-c2]]
[[legionloader-clickfix-malware]]
