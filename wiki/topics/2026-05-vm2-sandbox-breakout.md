---
slug: vm2-sandbox-breakout
first_seen: 2026-05-04
tags: [VM2, 샌드박스, RCE, Node.js]
cves: [CVE-2026-24781]
---

# VM2 샌드박스 탈출 및 원격 코드 실행

Node.js 샌드박스 **VM2** v3.11.0 이전 버전에서 inspect 함수를 악용한 취약점. 공격자가 VM 내부에서 작성한 코드가 inspect 함수를 통해 호스트 시스템에서 임의 명령을 실행할 수 있음. **CVSS 9.8** 중대 취약점.

## 타임라인

- 2026-05-04 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-24781) — CVE-2026-24781 공개 (CVSS 9.8)
