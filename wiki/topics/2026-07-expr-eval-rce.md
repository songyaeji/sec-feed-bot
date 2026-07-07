---
slug: expr-eval-rce
first_seen: 2026-07-07
tags: [취약점, 코드실행, npm]
cves: [CVE-2026-12866]
---

npm 패키지 **expr-eval** 모든 버전에서 Code Execution 취약점 발견. toJSFunction() API가 사용자 입력을 `new Function()`으로 직접 native code로 컴파일하면서 임의 JavaScript 실행 가능. 해당 패키지를 종속성으로 사용하는 모든 애플리케이션이 영향 대상.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-12866) — expr-eval 모든 버전 Code Execution 취약점 공개 (CVSS 9.8)

## 관련
