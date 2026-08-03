---
slug: glienet-command-injection
first_seen: 2026-08-03
tags: [라우터, 명령인젝션, 원격코드실행, RCE, 공개익스플로잇]
cves: [CVE-2026-18601]
---

# GL.iNet GL-MT3000 명령 주입 취약점

WiFi 라우터 **GL.iNet GL-MT3000** 4.4.5 이전 버전의 ovpn-client.so 네이티브 플러그인에서 filename 파라미터 검증 부재로 인한 명령 주입 취약점이 발견되었다. CVSS 9.8의 심각한 취약점으로, 원격 공격자가 /cgi-bin/glc 엔드포인트를 통해 임의 명령을 실행 가능하며, 공개 exploit이 존재한다.

## 타임라인

- 2026-08-03 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-18601) — CVE-2026-18601 공개 (CVSS 9.8, 공개 exploit 존재)

## 관련

없음
