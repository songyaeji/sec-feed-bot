---
slug: coder-workspace-auto-provision
first_seen: 2026-07-07
tags: [development platform, insufficient verification]
cves: [CVE-2026-44454]
---

Coder 원격 개발환경 플랫폼의 미인증 자동 프로비저닝 취약점. `mode=auto` 딥링크로 작업공간 생성 시 사용자 명시 확인 없이 공격자 제어 매개변수가 Terraform 프로비저닝에 전달됨. 임의 개발환경 생성 및 리소스 낭비 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44454) — CVE-2026-44454 공개 (CVSS 8.1)
