---
slug: restrictedpython-guard-bypass
first_seen: 2026-07-08
tags: [샌드박스우회, Python]
cves: [CVE-2026-55830]
---

신뢰할 수 없는 Python 코드 실행을 제한하는 RestrictedPython 8.3 이전 버전의 `check_function_argument_names()` 함수에서 위치 인자(positional argument)에 대한 보안 검증을 누락했다. 공격자가 protected guard hook을 우회할 수 있다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-55830) — CVE-2026-55830 (CVSS 8.3) 공개

## 관련

