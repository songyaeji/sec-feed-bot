---
slug: adfs-machine-dpapi-key-exposure
first_seen: 2026-07-07
tags: [ADFS, 인증우회, Golden_SAML, Enterprise]
cves: []
---

Microsoft **ADFS**(Active Directory Federation Services)의 인증서 수동 로테이션 시 설정 오류로 인해 **inactive 토큰 서명 키**가 Machine DPAPI에 남아있어 복구될 수 있는 공격 경로가 발견되었다. Mandiant 레드팀 발견으로, 기존 **Golden SAML** 공격의 새로운 변형이며 LSASS 모니터링 등 엔터프라이즈 감시 우회 특성을 지닌다.

## 타임라인

- 2026-07-07 [Google Cloud Blog](https://cloud.google.com/blog/topics/threat-intelligence/recovering-active-adfs-signing-keys-machine-dpapi/) — Mandiant 발견, ADFS 토큰 서명 키 Machine DPAPI 노출 공격 기법 공개

## 관련
