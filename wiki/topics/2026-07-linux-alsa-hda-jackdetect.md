---
slug: linux-alsa-hda-jackdetect
first_seen: 2026-07-08
tags: [Linux kernel, 오디오 드라이버, 에러 처리]
cves: [CVE-2026-53291]
---

Linux 커널 ALSA HDA Conexant 드라이버의 cx_probe() 함수에서 snd_hda_jack_detect_enable_callback() 반환값 검사 누락. 이 함수가 포인터를 반환하는데 실패 시 (예: 메모리 할당 오류) 에러 검사 없이 진행되어 NULL 역참조 또는 부분 초기화된 객체 접근 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53291) — CVE-2026-53291 공개 (CVSS 5.5)
