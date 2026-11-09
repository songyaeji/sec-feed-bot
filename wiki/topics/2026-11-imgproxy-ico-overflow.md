---
slug: imgproxy-ico-overflow
first_seen: 2026-11-08
tags: [버퍼오버플로우, 원격코드실행, 이미지처리, CVE-2026-123614]
cves: [CVE-2026-123614]
---

**imgproxy** 4.0.0~4.0.16의 ICO 이미지 로더에서 정수 오버플로우로 인한 힙 버퍼오버플로우 취약점이 발견되었다. 원격 공격자가 조작된 data_size 값을 포함한 ICO 이미지를 제출하면 vips/icoload.c의 메모리 할당이 래핑되어 힙 메모리가 손상되고, 프로세스 충돌 또는 원격코드실행이 가능하다.

## 타임라인

- 2026-11-08 [NVD CVE-2026-123614](https://nvd.nist.gov/vuln/detail/CVE-2026-123614) — imgproxy 4.0.0~4.0.16 ICO 로더 정수 오버플로우 힙 버퍼오버플로우 CVSS 9.8
