---
slug: prebid-server-ssrf
first_seen: 2026-07-29
tags: [Prebid, 실시간광고, SSRF, 미인증]
cves: [CVE-2026-54735]
---

실시간 광고 경매 서버 Prebid Server의 입찰자 어댑터(bidder adapters)에서 사용자 제공 매개변수를 아웃바운드 요청 URL에 부적절히 보간해 서버 측 요청 위조(SSRF) 취약점을 야기한다. 공격자가 내부 네트워크 서비스나 민감한 엔드포인트에 요청을 보낼 수 있으며, 버전 4.4.0에서 수정됐다.

## 타임라인

- 2026-07-29 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-54735) — CVE-2026-54735 공개, SSRF로 내부 네트워크 접근 (CVSS 10.0)
