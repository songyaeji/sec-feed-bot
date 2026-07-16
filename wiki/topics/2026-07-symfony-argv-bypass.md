---
slug: symfony-argv-bypass
first_seen: 2026-07-14
tags: [Symfony, 프레임워크, argv파싱, 환경변수조작]
cves: [CVE-2024-50340, CVE-2026-47767]
---

**Symfony** 5.4.46~5.4.51, 6.4.40 이전, 7.4.12 이전, 8.0.12 이전에서 CVE-2024-50340 fix를 우회하는 정규표현식. `parse_str()`과 웹 SAPI의 불일치를 악용해 $_GET이 비어 있으면서도 $_SERVER['argv']에는 공격자 제어 --env/--no-debug 플래그가 남아 APP_ENV/APP_DEBUG 변수 변조 가능(CVSS 9.8).

## 타임라인

- 2026-07-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-47767) — CVE-2026-47767 공개 (5.4.52, 6.4.40, 7.4.12, 8.0.12에서 수정)

## 관련

[[symfony-cve-2024-50340]]
