---
slug: siyuan-unicode2emoji-xss-rce
first_seen: 2026-08-15
tags: [XSS, RCE, 노트앱, 임의코드실행]
cves: [CVE-2026-73053]
---

# SiYuan — unicode2Emoji 함수 XSS 및 임의 코드 실행

개인용 노트 앱 **SiYuan** v3.7.4 이전 버전의 unicode2Emoji 함수에서 아이콘 생성 코드포인트 분기 출력이 충분히 sanitize되지 않는다. 공격자가 16진수로 인코딩한 마크업으로 문서 아이콘을 조작하면 Node.js 통합이 활성화된 렌더러에서 XSS 공격이 실행되어 호스트 시스템에서 임의 코드 실행 가능.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-73053) — CVE-2026-73053 CVSS 9.0 공개, unicode2Emoji XSS 및 RCE 취약점 확인
