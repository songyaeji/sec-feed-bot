---
slug: diskcache-pickle-rce
first_seen: 2026-07-08
tags: [Python, 라이브러리, 직렬화]
cves: [CVE-2025-69872]
---

Python 캐싱 라이브러리 **DiskCache** 5.6.3 이하에서 기본값으로 pickle 형식을 사용하면서, 캐시 디렉터리에 쓰기 권한이 있는 공격자가 악의적 객체를 삽입해 임의 코드 실행이 가능하다(CVSS 9.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-69872) — CVE-2025-69872 공개

## 관련
