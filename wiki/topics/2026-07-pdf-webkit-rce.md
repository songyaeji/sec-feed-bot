---
slug: pdf-webkit-rce
first_seen: 2026-08-13
tags: [Perl, 라이브러리, 인자주입]
cves: [CVE-2026-16770]
---

PDF::WebKit 1.2 이하 Perl 버전의 원본 문서 메타 태그 _pdf_webkit_meta_tags 처리에서 인자 주입이 발생한다. HTML 문자열 또는 파일 원본에서 <meta name="pdf-webkit-KEY" content="VALUE"> 요소를 수집하여 wkhtmltopdf 명령줄 옵션으로 변환하는데, KEY는 --[a-z0-9-]+ 패턴만 정규화되고 화이트리스트 검증이 없으며 VALUE는 그대로 전달된다. --enable-local-file-access나 --cookie-jar 같은 위험한 스위치를 문서가 재정의할 수 있다.

## 타임라인

- 2026-08-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16770) — CVE-2026-16770 CVSS 9.8 공개, 신뢰할 수 없는 HTML 인자 주입 취약점 확인
