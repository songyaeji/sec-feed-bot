---
slug: n2os-remote-collector-tls-mitm
first_seen: 2026-07-09
tags: [TLS, MITM, 설정오류, 암호화부재]
cves: [CVE-2026-31985]
---

# n2OS Remote Collector TLS 인증서 검증 비활성화 취약점

**n2OS** 원격 수집기(Remote Collector)에서 upstream Guardian 또는 CMC 설정 시 생성되는 설정이 TLS 인증서 검증을 비활성화하고 이를 활성화할 옵션을 제공하지 않음. 공격자가 중간자 공격(MITM)을 수행하여 Remote Collector와 upstream 서버 간 통신을 가로채고 데이터 탈취 또는 명령 조작 가능(CVSS 8.1).

## 타임라인

- 2026-07-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-31985) — CVE-2026-31985: n2OS Remote Collector TLS 검증 미작동
