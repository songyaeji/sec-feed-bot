---
slug: citrix-netscaler-memory-overread-8451
first_seen: 2026-06-30
tags: [Citrix, 메모리누출, 미인증접근, 로드밸런서]
cves: [CVE-2026-8451]
---

Citrix **NetScaler** 로드밸런서의 **메모리 오버리드**(over-read) 취약점 CVE-2026-8451('**CitrixBleed**')이 발견되었다. 미인증 원격 공격자가 메모리 내용 탈취 가능하여 인증서·토큰·암호 등 민감정보 노출 위험이 있다. 경계 기기 침해로 전사 영향.

## 타임라인

- 2026-06-30 [watchTowr Labs](https://labs.watchtowr.com/citrixbleed-to-infinity-and-beyond-citrix-netscaler-pre-auth-memory-overread-cve-2026-8451/) — watchTowr, Citrix NetScaler CVE-2026-8451 메모리 오버리드 취약점 분석

## 관련

[[citrix-netscaler-auth-bypass]] [[citrix-netscaler-rce-active-exploit]] [[citrix-netscaler-sept2026-zerodaya]]
