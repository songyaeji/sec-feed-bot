---
slug: npm-axios-supply-chain
first_seen: 2026-03-31
tags: [공급망공격, npm, UNC1069, 백도어]
cves: []
---

# Axios NPM 패키지 공급망 공격 — UNC1069 WAVESHAPER.V2 배포

북한 계열 위협 그룹 **UNC1069**이 인기 JavaScript HTTP 라이브러리 **Axios**의 NPM 패키지를 해킹해 악성 의존성을 삽입했다.
이를 통해 **WAVESHAPER.V2** 백도어를 Windows, macOS, Linux 시스템에 배포했다.
주간 다운로드 100+ 백만으로 광범위한 공급망 2차 피해 우려가 있다.

## 타임라인

- 2026-03-31 [Google Threat Intelligence](https://cloud.google.com/blog/topics/threat-intelligence/north-korea-threat-actor-targets-axios-npm-package/) — UNC1069의 Axios NPM 공급망 공격, plain-crypto-js 악성 의존성 삽입 및 WAVESHAPER.V2 백도어 배포 분석
- 2026-07-06 [KISA 보고서](https://www.boho.or.kr/kr/bbs/view.do?bbsId=B0000127&menuNo=&nttId=72122) — 해킹진단도구 활용 방안#7: AXIOS 공급망 공격을 통한 서버 침해 및 정보 유출
- 2026-11-21 [KISA 보고서/가이드](https://www.boho.or.kr/kr/bbs/view.do?searchCnd=&bbsId=B0000127&searchWrd=&menuNo=205021&pageIndex=1&categoryCode=&nttId=72122) — 해킹진단도구 활용 방안#7(AXIOS 공급망 공격을 통한 서버 침해 및 정보 유출)

## 관련

- [[2026-04-axios-no-proxy-bypass]]
- [[2026-07-kisa-pentool-vpn-breach]]
