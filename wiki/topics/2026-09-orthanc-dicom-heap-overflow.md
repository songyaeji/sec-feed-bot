---
slug: orthanc-dicom-heap-overflow
first_seen: 2026-09-10
tags: [의료기기, PNG취약점, 힙오버플로우]
cves: []
---

오픈소스 **Orthanc DICOM** 서버에서 PNG/JPEG 이미지 디코딩 시 힙 할당 경계를 넘는 쓰기(heap buffer overflow) 취약점이 발견되었다. 인증된 공격자가 악의적 이미지를 전송하면 Orthanc 프로세스를 충돌시켜 서비스 거부 상태를 유발할 수 있다.

## 타임라인

- 2026-09-10 [CISA ICS-CERT Advisories](https://www.cisa.gov/news-events/ics-medical-advisories/icsma-26-253-02) — Orthanc DICOM Server PNG/JPEG 디코딩 힙 오버플로우 보안 공지

## 관련
