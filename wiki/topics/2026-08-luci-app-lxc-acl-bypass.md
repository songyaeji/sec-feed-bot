---
slug: luci-app-lxc-acl-bypass
first_seen: 2026-08-13
tags: [ACL우회, OpenWrt, 컨테이너탈출, 루트권한]
cves: [CVE-2026-72842]
---

# OpenWrt LXC 플러그인 ACL 우회 취약점

**OpenWrt** **luci-app-lxc** 플러그인의 ACL 일관성 부족으로 낮은 권한의 **LuCI 사용자가 미인증 상태에서 백엔드 컨테이너 관리 루트에 접근**할 수 있다. 공격자가 lxc_name 파라미터에 경로 정규화 우회(/.%2E) 기법을 사용해 호스트 측 스크립트(lxc.hook.start-host)를 제어하고 **OpenWrt 호스트에서 루트 명령 실행**이 가능하다.

## 타임라인

- 2026-08-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-72842) — CVE-2026-72842 luci-app-lxc ACL inconsistency path traversal 공개 (CVSS 9.9)

## 관련

[[luci-app-openvpn-path-traversal]] — OpenWrt OpenVPN 플러그인 취약점
