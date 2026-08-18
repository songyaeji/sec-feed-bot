---
slug: siemens-simcenter-nastran-stack-overflow
first_seen: 2026-08-18
tags: [RCE, 스택오버플로우, 산업소프트웨어, CAD]
cves: []
---

# Siemens Simcenter Nastran — 스택 오버플로우 원격코드실행

Siemens Simcenter Nastran CAD 엔지니어링 소프트웨어의 애플리케이션 바이너리가 파일 인자로 수신한 임의 문자열 처리 시 스택 버퍼 오버플로우에 노출. 사용자가 악의적 파일로 실행하도록 속을 경우 프로세스 컨텍스트에서 원격 코드 실행 가능.

## 타임라인

- 2026-08-18 [CISA ICS Advisory](https://www.cisa.gov/news-events/ics-advisories/icsa-26-230-02) — 스택 오버플로우 취약점 공개 패치 배포
