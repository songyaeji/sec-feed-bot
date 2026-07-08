---
slug: fluentd-rce
first_seen: 2026-07-08
tags: [RCE, 데이터수집]
cves: [CVE-2026-44024]
---

Fluentd 1.19.3 이전 버전의 파일 출력 필터에서 `${tag}` placeholder를 사용한 경로 구성 시 검증이 부족해 원격 코드 실행(RCE)이 가능하다. 많은 데이터 수집 파이프라인이 영향받는다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44024) — CVE-2026-44024 (CVSS 9.8) 공개

## 관련

