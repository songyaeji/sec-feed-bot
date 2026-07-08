---
slug: linux-bnep-shortframe
first_seen: 2026-07-08
tags: [Linux, Bluetooth, 메모리 안전]
cves: [CVE-2026-53253]
---

Linux 커널 Bluetooth BNEP(Bluetooth Network Encapsulation Protocol) 처리에서 짧은 SDU 프레임에 대한 사전 검증 부재. BNEP 핸들러가 패킷 타입 바이트, 제어 옵코드, UUID 크기 바이트를 즉시 읽으면서 프레임 길이 확인 미실시. 공격자가 짧은 프레임 전송 시 범위 초과 접근으로 **NULL 포인터 역참조** 또는 메모리 손상 초래.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53253) — CVE-2026-53253 공개 (CVSS 7.1)

## 관련
