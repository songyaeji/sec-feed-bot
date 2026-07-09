---
slug: jackson-databind-array-bypass
first_seen: 2026-06-23
tags: [jackson-databind, Java, 역직렬화, 타입검증]
cves: [CVE-2026-54513]
---

# jackson-databind 배열 타입 검증 우회 취약점

**jackson-databind** v2.10.0~v2.18.8, v2.21.4, v3.1.4 버전에서 BasicPolymorphicTypeValidator.Builder.allowIfSubTypeIsArray()가 clazz.isArray()만 기반으로 배열 타입을 화이트리스트하여 타입 검증을 완벽하게 우회 가능. **CVSS 8.1**.

## 타임라인

- 2026-06-23 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54513) — CVE-2026-54513 공개 (CVSS 8.1)
