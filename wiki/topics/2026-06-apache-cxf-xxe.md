---
slug: apache-cxf-xxe
first_seen: 2026-06-12
tags: [Apache CXF, XML, XXE, 웹서비스]
cves: [CVE-2026-49875]
---

# Apache CXF XML 외부 엔티티 처리 취약점

**Apache CXF** EndpointReferenceUtils 및 W3CMultiSchemaFactory 클래스가 필요한 JAXP 강화 구성 없이 **SAXParserFactory**를 구성하여 OOB(Out-of-band) 외부 엔티티 해석이 가능한 취약점. v4.2.2 또는 v4.1.7 이상 업그레이드 권장.

## 타임라인

- 2026-06-12 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-49875) — CVE-2026-49875 공개
