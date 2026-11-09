---
slug: kyverno-authorization-bypass
first_seen: 2026-11-08
tags: [권한우회, 쿠버네티스, 클러스터권한탈취, CVE-2026-124440]
cves: [CVE-2026-124440]
---

**Kyverno** 쿠버네티스 정책 엔진의 apiCall 네임스페이스 필터에서 퍼센트 인코딩 우회로 인증된 테넌트가 다른 네임스페이스·클러스터 범위 API 요청을 실행할 수 있는 권한 우회 취약점이 발견되었다. 관리자 권한으로 실행되는 뮤테이팅 웹훅을 생성해 클러스터 관리자 권한을 탈취 가능하다.

## 타임라인

- 2026-11-08 [NVD CVE-2026-124440](https://nvd.nist.gov/vuln/detail/CVE-2026-124440) — Kyverno 1.19.1~1.19.2 apiCall 필터 퍼센트 인코딩 우회 권한상향 CVSS 9.9
