---
slug: plesk-xmlrpc-authbypass
first_seen: 2026-07-08
tags: [Plesk, 접근제어, XML-RPC]
cves: [CVE-2026-56843]
---

WebPros **Plesk** 18.0.78.4 이전 버전의 XML-RPC API 인증 검증 누락. 저권한 인증 고객이 소유하지 않은 도메인을 조회 가능하며, 특정 필터에서만 권한이 검증되고 레거시 프로토콜에서 **스키마 검증 우회**로 권한상향 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-56843) — CVE-2026-56843: XML-RPC API 인증 우회 (CVSS 9.9)

## 관련
