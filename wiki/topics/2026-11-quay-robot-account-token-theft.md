---
slug: quay-robot-account-token-theft
first_seen: 2026-11-11
tags: [Quay, 컨테이너레지스트리, SQL인젝션, 크로스테넌트, 토큰탈취]
cves: [CVE-2026-110697]
---

# Quay 로봇 계정 토큰 크로스-테넌트 탈취

**Quay** 컨테이너 레지스트리의 **CVE-2026-110697** (CVSS 9.9) SQL 인젝션 취약점. 로봇 계정 조회 함수가 SQL LIKE 패턴을 사용자 제어 namespace 명에서 escape 하지 않아, underscore 와일드카드 문자를 포함한 namespace를 생성하는 공격자가 다른 테넌트의 로봇 계정과 복호화된 인증 토큰을 탈취할 수 있다. 크로스-테넌트 credential 탈취 및 이미지 작업 권한 상승으로 이어진다.

## 타임라인

- 2026-11-11 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-110697) — CVE-2026-110697 공개 (CVSS 9.9)
