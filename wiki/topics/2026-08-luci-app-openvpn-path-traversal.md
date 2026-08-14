---
slug: luci-app-openvpn-path-traversal
first_seen: 2026-08-13
tags: [경로검증우회, OpenWrt, 라우터, 루트권한]
cves: [CVE-2026-72841]
---

# OpenWrt OpenVPN 플러그인 경로검증 우회

**OpenWrt** **luci-app-openvpn** 플러그인의 파일 업로드 처리에서 instance_name2 파라미터에 대한 경로 검증이 부족해 **경로 검증을 우회**할 수 있다. 인증된 공격자가 SSH 공개 키나 악성 스크립트를 시스템 디렉터리에 업로드해 **루트 권한**으로 지속성 있는 코드 실행 및 원격 접근이 가능하다.

## 타임라인

- 2026-08-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-72841) — CVE-2026-72841 luci-app-openvpn instance_name2 path traversal 공개 (CVSS 9.9)

## 관련

[[luci-app-lxc-acl-bypass]] — OpenWrt LXC 플러그인 취약점
