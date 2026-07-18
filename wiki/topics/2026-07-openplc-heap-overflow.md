---
slug: openplc-heap-overflow
first_seen: 2026-07-18
tags: [산업제어시스템, 버퍼오버플로우, PLC]
cves: [CVE-2026-11826]
---

OpenPLC_v3의 getData() 함수에서 경계 검사 없이 데이터를 버퍼에 읽는 힙 버퍼 오버플로우 취약점. mbconfig.cfg 로드 시 파싱되며 인접 구조체 필드(protocol, dev_address, ip_port)를 덮어쓸 수 있음. 인증된 공격자가 웹 인터페이스를 통해 원격 공격 가능. 상위 저장소는 2026년 4월에 아카이브되어 패치 예정 없음.

## 타임라인

- 2026-07-18 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-11826) — CVE-2026-11826 공개, OpenPLC Runtime v4는 영향받지 않음

## 관련

[[ics-ot-vulnerabilities]]
