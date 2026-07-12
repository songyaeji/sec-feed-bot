---
slug: linux-alsa-usb-midi2-descriptor
first_seen: 2026-06-24
tags: [커널버그, USB오디오, MIDI]
cves: [CVE-2026-52964]
---

Linux 커널 sound/usb의 USB MIDI 2.0 엔드포인트 파서에서 설명자 경계 검사 부재로 인한 범위 초과 메모리 접근. MIDI 레거시 파서와 유사하게 bNumGrpTrmBlock을 검증하지만 엔드포인트-엑스트라 스캔 남은 바이트 범위를 고려하지 않음. 악의적인 장치가 설명자 오버리드 야기 가능. 0 길이 및 범위 초과 설명자 거부 추가로 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52964) — Linux ALSA usb-audio 패치 공개

## 관련

[[linux-alsa-usb-midi-descriptor]]
