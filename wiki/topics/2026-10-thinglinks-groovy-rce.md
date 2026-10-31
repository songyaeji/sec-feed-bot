---
slug: thinglinks-groovy-rce
first_seen: 2026-10-30
tags: [원격코드실행, 미샌드박스스크립트, IoT플랫폼]
cves: [CVE-2026-62853]
---

ThingLinks 엔터프라이즈 IoT 플랫폼의 규칙 엔진 Groovy 스크립트 test/register 엔드포인트에서 사용자 입력 코드를 샌드박스 없이 컴파일·로딩하므로 인증된 공격자가 원격 코드 실행이 가능하다.

## 타임라인

- 2026-10-30 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-62853) — /groovyScriptTest/registerScript 엔드포인트 미샌드박스 Groovy 컴파일로 인증된 RCE 가능, 버전 1.4.0 이상에서 패치

## 관련

없음
