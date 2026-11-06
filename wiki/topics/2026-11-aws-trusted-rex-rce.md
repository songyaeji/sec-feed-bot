---
slug: aws-trusted-rex-rce
first_seen: 2026-11-06
tags: [AWS, 클라우드, 명령주입, 권한상향]
cves: [CVE-2026-122193]
---

**AWS Trusted Remote Execution(REX)** 2026-07-28 이전 버전의 SSM 문서 프로비저닝 스크립트의 OS 명령 주입 취약점으로, **Rex-RO/Rex-RW SSM 문서 호출 권한이 있는 사용자가 관리되는 인스턴스에서 root 권한으로 임의 명령 실행** 및 **Cedar 정책 무효화** 가능 (CVSS 9.9).

## 타임라인

- 2026-07-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-122193) — CVE-2026-122193 패치 (스크립트로 생성된 SSM 문서 삭제 권고)
- 2026-11-06 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-122193) — CVE-2026-122193 공개 (CVSS 9.9)

## 관련
