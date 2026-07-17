---
slug: hireflow-hardcoded-secretkey
first_seen: 2026-07-16
tags: [vulnerability, authentication, hardcoded-secret]
cves: [CVE-2026-45336]
---

채용 관리 시스템 HireFlow 1.2 이하에서 경직화된 비밀키 사용으로 인한 세션 쿠키 위조 취약점. 공개된 값을 알고 있는 공격자는 admin 권한의 세션을 만들 수 있다.

## 타임라인

- 2026-07-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-45336) — CVE-2026-45336 CVSS 10.0: Flask app.py의 경직화된 secret_key로 세션 쿠키 서명, 미인증 공격자가 role=admin 위조 쿠키 생성 가능

## 관련
