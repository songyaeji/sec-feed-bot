---
slug: zephyr-ipv4-parse-overflow
first_seen: 2026-07-12
tags: [스택오버플로우, 메모리손상, Zephyr]
cves: [CVE-2026-10666]
---

**Zephyr RTOS** parse_ipv4() 함수에서 포트 부분 문자열의 길이 검증 부재로 인한 스택 오버플로우 취약점. v1.9.0부터 v4.4.0까지 모든 버전 영향. 공격자가 제어 가능한 메모리 손상 및 제어 흐름 탈취 가능. DNS 설정, zsock_getaddrinfo() API, eswifi Wi-Fi 코프로세서 DNS 응답 등 여러 경로에서 접근 가능. CVSS 8.1.

## 타임라인

- 2026-07-12 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-10666) — CVE-2026-10666 공개, Zephyr 스택 오버플로우 취약점

## 관련
