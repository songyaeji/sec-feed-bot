---
slug: frogman-pbx-injection
first_seen: 2026-07-16
tags: [Frogman, PBX, 템플릿인젝션, Asterisk]
cves: [CVE-2026-46512]
---

**Frogman** 오픈소스 PBX 1.6.2 이전 버전에서 fm_dialplan_apply가 설정 파라미터를 제대로 검증하지 않아, 인증된 공격자가 임의 Asterisk 지시자(System(), Set(SHELL(...)), Goto, Macro)를 주입해 서버 명령 실행이 가능(CVSS 9.9).

## 타임라인

- 2026-07-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46512) — CVE-2026-46512 공개, Frogman 1.6.2에서 수정
