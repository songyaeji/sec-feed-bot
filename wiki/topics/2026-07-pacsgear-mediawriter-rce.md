---
slug: pacsgear-mediawriter-rce
first_seen: 2026-07-01
tags: [RCE, 의료기기, .NET원격처리, 역직렬화, 무인증]
cves: [CVE-2026-58127]
---

# PACSgear MediaWriter 미디어 관리 도구 원격코드실행

의료 영상 미디어 작성·관리 도구 PACSgear MediaWriter v5.2.1에서 발견된 중대 취약점. 노출된 **.NET Remoting TCP 서비스**(포트 9000, **PacsgearMediaServerEngine.dll**, RemoteObj/UIRemoteObj)가 인증 없이 **MarshalByRefObject** 객체 역직렬화 공격에 취약하여 원격 코드 실행 가능(CVSS 9.8).

## 타임라인

- 2026-07-01 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-58127) — CVE-2026-58127: PACSgear MediaWriter v5.2.1 port 9000 .NET Remoting 역직렬화 RCE
