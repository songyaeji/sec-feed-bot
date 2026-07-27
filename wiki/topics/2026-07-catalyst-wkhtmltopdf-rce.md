---
slug: catalyst-wkhtmltopdf-rce
first_seen: 2026-07-27
tags: [Perl, Catalyst, wkhtmltopdf, 쉘명령인젝션, 원격코드실행]
cves: [CVE-2026-16766]
---

Perl Catalyst 웹 프레임워크의 View::Wkhtmltopdf 모듈 0.6.1 이전 버전에서 PDF 렌더 옵션이 wkhtmltopdf 명령에 정제 없이 전달되는 문제. 사용자가 제어 가능한 옵션(page_size, orientation, margins)을 통해 쉘 메타문자를 주입해 임의 명령을 실행할 수 있다. 버전 0.6.0의 불완전한 수정 후 0.6.1에서 재수정됨. CVSS 9.8로 평가됨.

## 타임라인

- 2026-07-25 — 취약점 발견
- 2026-07-27 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16766) — CVE-2026-16766 공개
