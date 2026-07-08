---
slug: grpc-go-http2-authbypass
first_seen: 2026-07-08
tags: [gRPC, 인증, 클라우드]
cves: [CVE-2026-33186]
---

Go 기반 gRPC 구현 **gRPC-Go** 1.79.3 이전 버전에서 HTTP/2 :path 의사헤더 검증이 부족하다. 라우팅 로직이 필수 경로 접두어를 생략한 요청을 수용해 권한 없는 API 호출이 가능하다(CVSS 9.1).

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-33186) — CVE-2026-33186 공개

## 관련
