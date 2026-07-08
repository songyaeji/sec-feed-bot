---
slug: horde-vfs-smb-injection
first_seen: 2026-07-08
tags: [RCE, 명령삽입]
cves: [CVE-2026-60102]
---

**Horde Virtual File System (VFS) API** 3.0.1 이전에서 SMB 드라이버의 명령 삽입 취약점. `Horde_Vfs_Smb` 드라이버의 `_escapeShellCommand()` 메서드가 사용자 입력의 명령 치환 시퀀스를 제대로 이스케이프하지 않음. **인증된 공격자**가 사용자 입력을 조작하여 **임의 셀 명령 실행** 가능. Horde 파일 관리 기능을 통한 서버 침해.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-60102) — CVE-2026-60102 공개 (CVSS 8.8)

## 관련
