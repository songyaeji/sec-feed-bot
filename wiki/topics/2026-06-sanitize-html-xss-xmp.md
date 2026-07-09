---
slug: sanitize-html-xss-xmp
first_seen: 2026-06-12
tags: [sanitize-html, XSS, HTML, Node.js]
cves: [CVE-2026-44990]
---

# sanitize-html XMP 요소 우회 XSS 취약점

HTML 살균 라이브러리 **sanitize-html** v2.17.4 이전 버전에서 기본 구성 상태에서 허용 금지된 **xmp 요소** 내부의 공격자 제어 콘텐츠를 라이브 HTML로 변환 가능. **CVSS 9.3** 심각한 XSS 취약점.

## 타임라인

- 2026-06-12 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44990) — CVE-2026-44990 공개 (CVSS 9.3)
