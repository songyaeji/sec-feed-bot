---
slug: linux-kernel-kvm-arm64-escape
first_seen: 2026-09-22
tags: [커널취약점, 가상화회피, ARM64, 게스트탈출, 메모리노출]
cves: [CVE-2026-89775]
---

Linux 커널 **KVM 가상화** ARM64 프로세서 **메모리 사용 후 해제(Use-After-Free)** 취약점(CVE-2026-89775). 중첩 가상화 활성 호스트의 게스트 VM이 호스트 커널 메모리 읽기·쓰기 가능해 **게스트 탈출(VM Escape)** 및 호스트 코드 실행 가능.

## 타임라인

- 2026-09-22 [The Hacker News](https://thehackernews.com/2026/09/new-linux-kernel-flaw-gives-arm64-kvm.html) — Linux KVM ARM64 메모리 노출 CVE-2026-89775 게스트 탈출 가능
