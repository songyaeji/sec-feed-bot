---
slug: zephyr-websocket-memory
first_seen: 2026-07-08
tags: [Zephyr, RTOS, IoT, 메모리 손상]
cves: [CVE-2026-5067]
---

**Zephyr** RTOS의 HTTP 서버 WebSocket 업그레이드 경로에서 `Sec-WebSocket-Key` 헤더 처리 시 고정 크기 버퍼에 경계 검증 없는 복사 수행. HTTP/1 헤더 파서의 정제되지 않은 입력으로 메모리 손상 유발 가능(CVSS 9.8).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-5067) — CVE-2026-5067 공개 (CVSS 9.8)

## 관련
