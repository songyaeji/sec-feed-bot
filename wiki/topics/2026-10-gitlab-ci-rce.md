---
slug: gitlab-ci-rce
first_seen: 2026-10-13
tags: [개발도구보안, CI/CD공격, 원격코드실행]
cves: [CVE-2026-97229]
---

**GitLab** CE/EE의 CI/CD 설정에서 정규표현식 검증 미흡으로 미인증 공격자가 특수 제작된 정규표현식을 통해 GitLab 서버에서 임의 코드 실행 가능하다. 기록적 위협이며 광범위 DevOps 인프라를 대상으로 한다.

## 타임라인

- 2026-10-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-97229) — CVE-2026-97229 공개, GitLab CI/CD 정규표현식 원격코드실행 (CVSS 10.0)

## 관련

[[gitlab-path-traversal-cve-2023-2825]]
