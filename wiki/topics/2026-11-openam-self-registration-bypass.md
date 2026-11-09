---
slug: openam-self-registration-bypass
first_seen: 2026-11-08
tags: [인증우회, 권한상향, 관리자탈취, CVE-2026-123549]
cves: [CVE-2026-123549]
---

**OpenAM** 16.1.4 이전 자가-등록 기능에서 Valid Creation Attributes 목록 검증이 미작동한다. 미인증 공격자가 레거시 자가-서비스 REST 엔드포인트 또는 사용자 자가-서비스 흐름으로 등록하면서 제한된 속성(그룹 멤버십 포함)을 직접 설정해 관리자 그룹에 가입하고 **OpenAM 전체 관리자 권한을 획득**할 수 있다.

## 타임라인

- 2026-11-08 [NVD CVE-2026-123549](https://nvd.nist.gov/vuln/detail/CVE-2026-123549) — OpenAM 16.1.4 이전 자가-등록 검증 우회로 관리자 권한 획득 CVSS 9.8
