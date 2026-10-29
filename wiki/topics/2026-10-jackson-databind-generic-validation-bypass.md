---
slug: jackson-databind-generic-validation-bypass
first_seen: 2026-10-28
tags: [jackson-databind, Java, 역직렬화, 검증우회]
cves: [CVE-2026-110879, CVE-2026-54512]
---

jackson-databind에서 클래스명 타입 ID의 외부 클래스는 검증하지만 제네릭 인자 내부의 클래스는 검증하지 않아, CVE-2026-54512의 불완전한 수정을 우회할 수 있다. CVSS 9.8으로 제한된 인자 타입도 검증 실패해 임의 객체 생성이 가능하며, Java 생태계 광범위 RCE로 이어질 수 있다.

## 타임라인

- 2026-06-23 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54512) — CVE-2026-54512 공개, 배열 타입 검증 우회
- 2026-10-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-110879) — CVE-2026-110879 공개 (CVSS 9.8), CVE-2026-54512의 불완전한 수정 우회

## 관련

[[jackson-databind-array-bypass]]
