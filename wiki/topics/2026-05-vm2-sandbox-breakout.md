---
slug: vm2-sandbox-breakout
first_seen: 2026-05-04
tags: [VM2, 샌드박스, RCE, Node.js]
cves: [CVE-2026-24781, CVE-2026-43997, CVE-2026-44005, CVE-2026-44006, CVE-2026-43999]
---

# VM2 샌드박스 탈출 및 원격 코드 실행

Node.js 샌드박스 **VM2** v3.11.0 이전 버전에서 여러 경로의 샌드박스 탈출 취약점. 공격자가 VM 내부에서 작성한 코드가 프로토타입 오염·모듈 로딩·intrinsic 접근 등을 악용해 호스트 시스템에서 임의 명령을 실행할 수 있음. **CVSS 10.0** 중대 취약점.

## 타임라인

- 2026-05-04 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-24781) — CVE-2026-24781 공개 (CVSS 9.8)
- 2026-05-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-43997) — CVE-2026-43997 Host Object 접근 (CVSS 10.0)
- 2026-05-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44005) — CVE-2026-44005 프로토타입 오염 (CVSS 10.0)
- 2026-05-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44006) — CVE-2026-44006 BaseHandler.getPrototypeOf (CVSS 10.0)
- 2026-05-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-43999) — CVE-2026-43999 module builtin 우회 (CVSS 9.9)
- 2026-08-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-47686) — CVE-2026-47686 Error.cause 검증 누락 호스트 객체 접근 (CVSS 9.9)
