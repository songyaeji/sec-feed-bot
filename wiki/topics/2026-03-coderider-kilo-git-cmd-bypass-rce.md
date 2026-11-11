---
slug: coderider-kilo-git-cmd-bypass-rce
first_seen: 2026-03-27
tags: [명령인젝션, 원격코드실행, Git도구, 윈도우탈출]
cves: [CVE-2026-30302]
---

# CodeRider-Kilo Git 명령 검증 우회

**CodeRider-Kilo** 개발 도구의 명령 자동 승인 모듈(**CVE-2026-30302**, CVSS 10.0)에서 발견된 OS 명령 인젝션 취약점. Unix 기반 shell-quote 라이브러리와 Windows CMD 이스케이프 시퀀스 처리의 불일치를 악용해 whitelist를 무력화하고 임의 명령을 실행할 수 있다.

## 타임라인

- 2026-03-27 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-30302) — CVE-2026-30302 공개 (CVSS 10.0)
