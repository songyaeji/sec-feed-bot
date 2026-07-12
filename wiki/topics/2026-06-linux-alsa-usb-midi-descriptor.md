---
slug: linux-alsa-usb-midi-descriptor
first_seen: 2026-06-24
tags: [커널버그, USB오디오, 경계검사]
cves: [CVE-2026-52963]
---

Linux 커널 sound/usb의 `snd_usbmidi_get_ms_info()` 함수에서 MIDI 엔드포인트 설명자 스캔 경계 검사 부재로 인한 범위 초과 메모리 접근. 클래스별 엔드포인트 설명자 검증 후에도 바이너리 데이터 읽기가 남은 바이트 수를 초과할 수 있음. 설명자 워커에 bLength 0 및 범위 초과 거부 추가로 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52963) — Linux ALSA usb-audio 패치 공개

## 관련

[[linux-alsa-usb-midi2-descriptor]]
