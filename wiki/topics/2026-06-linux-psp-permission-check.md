---
slug: linux-psp-permission-check
first_seen: 2026-06-24
tags: [네트워킹, 권한검증, netlink]
cves: [CVE-2026-52978]
---

Linux PSP(Packet Security Protocol) 네트워크 드라이버의 dev-set 및 key-rotate netlink 작업에서 CAP_NET_ADMIN 권한 검증 부재. psp_dev_check_access()만으로 네임스페이스 멤버십만 확인하고 공유 디바이스 상태(PSP 버전 설정, 암호화 키) 수정 권한 제어 없음.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52978) — net psp CAP_NET_ADMIN 권한 검증 부재 공개

## 관련
