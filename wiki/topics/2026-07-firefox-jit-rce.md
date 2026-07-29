---
slug: firefox-jit-rce
first_seen: 2026-07-29
tags: [Firefox, 브라우저, RCE, 웹보안]
cves:
  - CVE-2026-10702
---

Firefox의 JIT 컴파일 취약점이 151.0.3에서 패치되었다. 사용자가 악성 웹페이지를 방문하기만 해도 브라우저 렌더러 프로세스 내에서 임의코드를 실행할 수 있으며, 추가 상호작용이나 설정이 필요없다. Tor Browser도 동일 취약점의 영향을 받았다.

## 타임라인

- 2026-07-29 [The Hacker News](https://thehackernews.com/2026/07/researchers-show-single-malicious.html) — Firefox JIT 취약점 패치, Tor Browser 영향, CVE-2026-10702 (High)

## 관련

[[firefox-148-sandbox-escapes]] — Firefox 샌드박스 탈출 취약점
