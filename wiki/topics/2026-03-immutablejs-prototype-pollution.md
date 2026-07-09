---
slug: immutablejs-prototype-pollution
first_seen: 2026-03-06
tags: [JavaScript, 라이브러리, 프로토타입오염]
cves: [CVE-2026-29063]
---

# Immutable.js 프로토타입 오염 취약점

JavaScript 불변 데이터 구조 라이브러리 **Immutable.js**의 `mergeDeep()`, `mergeDeepWith()`, `merge()`, `Map.toJS()`, `Map.toObject()` API에서 프로토타입 오염 취약점 발견(CVSS 9.8). 공격자가 임의 속성을 객체 프로토타입에 주입 가능.

## 타임라인

- 2026-03-06 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-29063) — CVE-2026-29063: Immutable.js 3.8.3, 4.3.7, 5.1.5 이상 버전에서 수정
