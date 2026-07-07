---
slug: linux-alsa-pcm-wait-queue
first_seen: 2026-07-07
tags: [Linux kernel, audio subsystem, wait queue, DoS]
cves: [CVE-2026-53242]
---

Linux 커널 ALSA PCM의 대기열 손상 취약점. snd_pcm_drain()이 링크된 스트림의 대기열에서 list 엔트리 초기화 시 prev/next를 초기화하지 않아 메모리 손상 유발 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53242) — CVE-2026-53242 공개 (CVSS 7.8)
