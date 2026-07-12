---
slug: linux-af-alg-aead-overflow
first_seen: 2026-06-24
tags: [암호화, 산술오버플로우, 소켓]
cves: [CVE-2026-52972]
---

Linux 암호 소켓 인터페이스(af_alg) AEAD(인증 암호화) 구현에서 TX 버퍼 크기 검사 시 산술 오버플로우 방지 목적으로 관련 데이터(AD) 길이를 0x80000000으로 캡핑.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52972) — af_alg AEAD AD 길이 산술 오버플로우 공개

## 관련
