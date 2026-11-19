---
slug: feast-udf-deserialization-rce
first_seen: 2026-08-10
tags: [역직렬화, RCE, 머신러닝, 데이터기반, 교차테넌트]
cves: [CVE-2026-18948]
---

오픈소스 **Feast** 머신러닝 피처 플랫폼에서 사용자정의함수(UDF) 역직렬화 취약점(CVSS 9.9)이 발견됐다. dill 라이브러리로 직렬화된 UDF를 미검증 역직렬화해 악의적 UDF를 registry에 저장하면 feature server에서 미인증 원격코드실행이 가능하고, registry 서버의 권한 검증 부재로 인증된 공격자는 교차테넌트 데이터 접근과 측횡 이동이 가능하다.

## 타임라인

- 2026-08-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-18948) — CVE-2026-18948 (CVSS 9.9) Feast 미인증 UDF 역직렬화 원격코드실행, registry 서버 권한 검증 우회 교차테넌트 접근 가능

## 관련
