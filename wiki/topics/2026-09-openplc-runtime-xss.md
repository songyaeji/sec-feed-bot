---
slug: openplc-runtime-xss
first_seen: 2026-09-22
tags: [산업제어시스템, OpenPLC, XSS, 세션쿠키탈취, CVSS-6.1]
cves: [CVE-2026-88020]
---

**OpenPLC Runtime v3**에서 웹 인터페이스 입력 검증 취약점 **CVE-2026-88020** 발견. 공격자가 쿼리 문자열 변수의 인코딩 부재를 악용해 세션 쿠키 탈취 및 PLC 제어 권한 획득 가능. OpenPLC v3는 단종 상태로 패치 미지원.

## 타임라인

- 2026-09-22 [CISA ICS Advisory ICSA-26-265-09](https://www.cisa.gov/news-events/ics-advisories/icsa-26-265-09) — OpenPLC Runtime v3 XSS 취약점 공개, Autonomy Logic이 v4 업그레이드 권고

## 관련
