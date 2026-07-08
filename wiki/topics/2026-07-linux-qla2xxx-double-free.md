---
slug: linux-qla2xxx-double-free
first_seen: 2026-07-08
tags: [커널, SCSI, 이중해제]
cves: [CVE-2026-43414]
---

Linux 커널의 SCSI qla24xx 드라이버에서 `qla24xx_els_dcmd_iocb()` 함수의 스트럭처 포인터 해제 콜백이 두 번 호출되는 이중 해제 취약점. 오류 경로에서 `kref_put()`이 첫 번째 해제 후에도 다시 실행되어 힙 손상 및 권한상향 위험이 있다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-43414) — CVE-2026-43414 공개 (CVSS 9.8)
