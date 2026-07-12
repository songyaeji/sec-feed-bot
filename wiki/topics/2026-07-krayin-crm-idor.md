---
slug: krayin-crm-idor
first_seen: 2026-07-10
tags: [IDOR, CRM, 데이터변조]
cves: [CVE-2026-61460]
---

**Krayin CRM** 관계관리 시스템(≤ 2.2.3) IDOR(Insecure Direct Object Reference) 취약점. LeadController, PersonController, OrganizationController, QuoteController, ActivityController의 edit, update, destroy 메서드가 레코드 소유권 검증 부재. 인증 사용자가 다른 사용자 소유 레코드 편집·업데이트·삭제 가능. CRM 레코드 수정 및 소유권 재할당 가능 (CVSS 8.8).

## 타임라인

- 2026-07-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-61460) — CVE-2026-61460 공개

## 관련
