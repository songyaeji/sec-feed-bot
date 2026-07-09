---
slug: ace-kernel-privesc
first_seen: 2024-05-01
tags: [권한상향, 커널, 접근제어]
cves: [CVE-2024-22830]
---

# Anti-Cheat Expert 커널 드라이버 권한상향 취약점

안티치트 솔루션 Anti-Cheat Expert의 Windows 커널 모듈 **ACE-BASE.sys** v1.0.2202.6217에서 발견된 권한상향 취약점. 시스템 리소스 접근 제어 미검증으로 일반 사용자가 System 또는 PPL(Process Protection Level) 수준으로 권한 상향 가능(CVSS 5.3).

## 타임라인

- 2024-05-01 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-22830) — CVE-2024-22830: ACE-BASE.sys 접근 제어 미검증 권한상향
