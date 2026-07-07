---
slug: linux-fastrpc-null-deref
first_seen: 2026-07-07
tags: [Linux kernel, NULL pointer dereference]
cves: [CVE-2026-53158]
---

Linux 커널 fastrpc 드라이버의 rpmsg 콜백 NULL 포인터 역참조. Qualcomm 플랫폼에서 DSP가 초기화 완료 전에 glink 메시지를 전송할 때 fastrpc_rpmsg_probe()가 완료되지 않아 NULL 포인터 역참조로 부팅 중 시스템 중단 발생.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53158) — CVE-2026-53158 공개 (CVSS 5.5)
