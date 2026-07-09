---
slug: lodash-template-rce
first_seen: 2026-03-31
tags: [lodash, RCE, JavaScript, CVE-2021-23337]
cves: [CVE-2026-4800, CVE-2021-23337]
---

# lodash 템플릿 엔진 코드 실행 취약점

**lodash** 라이브러리의 CVE-2021-23337 패치가 _.template의 variable 옵션만 검증했으나, options.imports 키 이름에는 동일한 검증을 적용하지 않아 Function() 생성자 sink를 거쳐 임의 코드 실행 가능. **CVSS 8.1**.

## 타임라인

- 2026-03-31 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-4800) — CVE-2026-4800 공개 (CVSS 8.1)
