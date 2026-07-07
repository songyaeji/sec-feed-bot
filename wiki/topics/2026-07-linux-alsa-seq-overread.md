---
slug: linux-alsa-seq-overread
first_seen: 2026-07-07
tags: [Linux kernel, audio subsystem, stack buffer]
cves: [CVE-2026-53241]
---

Linux 커널 ALSA 시퀀서 더미 포트의 스택 버퍼 오버리드 취약점. 이벤트 포워딩 시 UMP 이벤트를 스택 임시 버퍼에 복사할 때 크기 검증 없이 snd_seq_event 구조체를 읽어 버퍼 오버플로우 발생 가능.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53241) — CVE-2026-53241 공개 (CVSS 5.5)
