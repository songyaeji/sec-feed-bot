---
slug: apache-roller-xmlrpc-auth
first_seen: 2026-09-28
tags: [권한검사미흡, API취약점, 블로깅플랫폼]
cves: [CVE-2026-82377]
---

# Apache Roller — XML-RPC 권한 검사 미흡

블로깅 플랫폼 **Apache Roller** 6.1.5의 XML-RPC Blogger·MetaWeblog API에서 **권한 검사 미흡** 취약점이 발견됐다. 인증은 되지만 권한 검증이 없어 타 블로그 콘텐츠를 읽고 수정·삭제할 수 있다.

## 타임라인

- 2026-09-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-82377) — CVE-2026-82377 CVSS 9.9 공개, XML-RPC API 권한 검사 미흡 확인

## 관련
