---
slug: totolink-a6000r-injection
first_seen: 2024-06-20
tags: [RCE, 라우터, 명령인젝션]
cves: [CVE-2024-37626]
---

# TOTOLINK A6000R 라우터 펌웨어 명령 인젝션 취약점

TOTOLINK A6000R v1.0.1 라우터 펌웨어에서 발견된 명령 인젝션 취약점. **vif_enable** 함수의 **iface** 파라미터 검증 부재로 원격 공격자가 임의 명령 실행 가능(CVSS 8.8).

## 타임라인

- 2024-06-20 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2024-37626) — CVE-2024-37626: TOTOLINK A6000R v1.0.1 vif_enable 함수 명령 인젝션
