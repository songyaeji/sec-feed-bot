---
slug: capgo-acl-bypass
first_seen: 2026-07-08
tags: [Capgo, 접근제어, API]
cves: [CVE-2026-56246]
---

앱 관리 플랫폼 **Capgo** 12.128.2 이전의 조직 관리 API에서 제한된 API 키(limited_to_orgs)가 소유자 사용자의 권한을 상속받으면서 **조직 간 권한 우회** 가능. 관리자가 여러 조직에서 활동할 때 이들 조직 사이에 **파괴적 작업** 실행 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-56246) — CVE-2026-56246: API 키 권한 상속 (CVSS 8.1)

## 관련
