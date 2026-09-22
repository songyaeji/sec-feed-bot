---
slug: sharepoint-authenticated-rce
first_seen: 2026-09-22
tags: [RCE, 원격코드실행, 인증필요, CVE분류오류, 마이크로소프트]
cves: [CVE-2026-65660]
---

Microsoft **SharePoint Server** 취약점 CVE-2026-65660. Microsoft가 CVSS 6.5 "스푸핑" 취약점으로 초기 분류했으나, 실제는 **인증된 사용자로부터 원격코드 실행** 가능. 영향 받는 버전: SharePoint Server 2016, 2019, Subscription Edition. 상세 기술 자료 공개로 악용 위협 증대.

## 타임라인

- 2026-09-22 [The Hacker News](https://thehackernews.com/2026/09/sharepoint-flaw-initially-listed-as.html) — SharePoint CVE-2026-65660 Microsoft 분류 오류 실제는 인증 RCE
