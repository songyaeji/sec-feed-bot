---
slug: openfunction-privilege-escalation
first_seen: 2026-11-17
tags: [권한상향, 쿠버네티스, 서버리스]
cves: [CVE-2026-130587]
---

**OpenFunction** 1.2.0 이상의 Function/Serving 리소스에서 PodSpec 템플릿 검증 없이 호스트 접근 권한 설정 가능. 함수 생성 권한만으로 호스트 root 접근 가능해 쿠버네티스 클러스터 완전 침해. CVSS 9.9로 서버리스 플랫폼 테넌트 격리 우회 위협.

## 타임라인

- 2026-11-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-130587) — CVE-2026-130587 OpenFunction 미검증 PodSpec 테넌트 권한상향 CVSS 9.9

## 관련

- [[kubernetes-security-vulnerabilities]]
