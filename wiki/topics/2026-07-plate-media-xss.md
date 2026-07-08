---
slug: plate-media-xss
first_seen: 2026-07-08
tags: [XSS, 텍스트에디터]
cves: [CVE-2026-55596]
---

**Plate** (shadcn/ui 기반 리치 텍스트 에디터) 53.0.0~53.1.4 버전의 미디어 임베드 렌더러가 직렬화된 provider/sourceUrl 메타데이터를 검증하지 않고 신뢰하여, 공격자가 알려진 비디오 제공자를 설정하면서 URL을 악의적 값으로 유지할 수 있는 취약점. 문서 클릭 시 XSS가 실행된다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-55596) — CVE-2026-55596 공개 (CVSS 8.7)
