---
slug: kludex-starlette-smuggling
first_seen: 2026-09-02
tags: [CISA KEV, Starlette, 웹프레임워크, 인증우회]
cves: [CVE-2026-48710]
---

**Kludex Starlette** 웹프레임워크의 HTTP 요청/응답 스머글링 취약점. 공격자가 호스트 부분에 경로를 주입해 실제 경로를 앞에 놓을 수 있으며, 재구성된 URL의 경로에 따라 인증이 달라지는 경우 인증 우회 가능. CISA KEV 게재.

## 타임라인

- 2026-09-02 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2026-48710) — CVE-2026-48710 Kludex Starlette HTTP 요청/응답 스머글링 공개

## 관련
