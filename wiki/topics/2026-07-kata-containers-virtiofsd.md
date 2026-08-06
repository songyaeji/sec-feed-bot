---
slug: kata-containers-virtiofsd
first_seen: 2026-07-23
tags: [Kata, 클라우드, 컨테이너, 권한상향]
cves: [CVE-2026-44210]
---

# Kata Containers - virtiofsd 공지 인젝션으로 호스트 파일시스템 접근

**CVE-2026-44210** Kata Containers v3.31.0 이전 버전에서 기본 설정이 pod 생성자로부터 `io.katacontainers.config.hypervisor.virtio_fs_extra_args` 주석을 통해 virtiofsd 프로세스로 임의 인자를 주입 가능. 공격자가 호스트 루트 파일시스템을 게스트 VM으로 공유하고 /etc/shadow 같은 민감 파일 읽기/쓰기 가능. **CVSS 9.9** 중대 취약점.

## 타임라인

- 2026-07-23 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-44210) — CVE-2026-44210 공개 (CVSS 9.9)
